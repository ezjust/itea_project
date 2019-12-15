import telebot
import bot.config as config
from models.cats_and_products import Texts, Category, Basket, OrdersHistory
from models.user_model import User
from mongoengine import connect
from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)
from bson import ObjectId


connect('bot_shop')

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def greetings(message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(*config.START_KEYBOARD.values())
    User.get_create_user(message)
    greetings_str = Texts.get_text('Greetings')
    bot.send_message(message.chat.id, 'Hello\n' + greetings_str, reply_markup=kb)


@bot.message_handler(func=lambda message: message.text == config.START_KEYBOARD['categories'])
def show_categories(message):
    cats_kb = InlineKeyboardMarkup()
    cats_buttons = []
    all_cats = Category.objects.all()

    for i in all_cats:
        callback_data = 'category_' + str(i.id)

        if i.is_parent:
            callback_data = 'subcategory_' + str(i.id)
        cats_buttons.append(InlineKeyboardButton(text=i.title,
                                                 callback_data=callback_data))

    cats_kb.add(*cats_buttons)
    bot.send_message(message.chat.id, text='Categories', reply_markup=cats_kb)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'subcategory')
def show_sub_cat(call):
    sub_cats_kb = InlineKeyboardMarkup()
    sub_cats_buttons = []
    cat_to_use = Category.objects.get(id=call.data.split('_')[1])
    print(cat_to_use.sub_categories)

    for i in cat_to_use.sub_categories:
        callback_data = 'category_' + str(i.id)

        if i.is_parent:
            callback_data = 'subcategory_' + str(i.id)
        sub_cats_buttons.append(InlineKeyboardButton(text=i.title, callback_data=callback_data))

    sub_cats_kb.add(*sub_cats_buttons)
    bot.send_message(call.message.chat.id, text='Sub Categories', reply_markup=sub_cats_kb)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'category')
def products_by_cat(call):
    cat = Category.objects.filter(id=call.data.split('_')[1]).first()
    products = cat.category_products

    if not products:
        bot.send_message(call.message.chat.id, "Category doesn't contain products")

    for p in products:
        products_kb = InlineKeyboardMarkup(row_width=2)
        products_kb.add(InlineKeyboardButton(text='Add to basket', callback_data=f'addtobasket_{str(p.id)}'))
        InlineKeyboardButton('Get full info', callback_data='product_' + str(p.id))

        title = f'<b>{p.title}</b>'
        description = f'<i>\n\n{p.description}</i>'

        bot.send_photo(call.message.chat.id, p.image.get(),
                       caption=f'{title + description}', reply_markup=products_kb, parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'addtobasket')
def add_to_basket(call):
    Basket.create_append_to_basket(product_id=call.data.split('_')[1], user_id=call.message.chat.id)
    basket = Basket.objects.all().first()


@bot.message_handler(func=lambda message: message.text == config.START_KEYBOARD['basket'])
def show_basket(message):
    current_user = User.objects.get(user_id=message.chat.id)
    basket = Basket.objects.filter(user=current_user, is_archieved=False).first()

    if not basket:
        bot.send_message(message.chat.id, 'Basket is empty')
        return

    if not basket.products:
        bot.send_message(message.chat.id, 'Basket is empty')

    for product in basket.products:
        remove_kb = InlineKeyboardMarkup()
        remove_button = InlineKeyboardButton(text='Remove from basket', callback_data='rmproduct_' + str(product.id))
        remove_kb.add(remove_button)
        bot.send_message(message.chat.id, product.title, reply_markup=remove_kb)

    submit_kb = InlineKeyboardMarkup()
    submit_button = InlineKeyboardButton(text='Make an Order', callback_data='submit')
    submit_kb.add(submit_button)
    bot.send_message(message.chat.id, 'Click to apply an order', reply_markup=submit_kb)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'rmproduct')
def rm_product_from_basket(call):
    current_user = User.objects.get(user_id=call.message.chat.id)
    basket = Basket.objects.get(user=current_user)
    basket.update(pull__products=ObjectId(call.data.split('_')[1]))
    bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'submit')
def submit_basket(call):
    current_user = User.objects.get(user_id=call.message.chat.id)
    basket = Basket.objects.filter(user=current_user, is_archieved=False).first()
    basket.is_archived = True

    order_history = OrdersHistory.get_or_create(current_user)
    order_history.cart.append(basket)
    bot.send_message(call.message.chat.id, 'Thanks for your order')
    basket.save()
    order_history.save()


if __name__ == '__main__':
    print('Bot started')
    bot.remove_webhook()
    bot.polling(none_stop=True)
