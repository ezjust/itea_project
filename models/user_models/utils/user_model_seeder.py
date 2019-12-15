import random
import string
from models.cats_and_products import Category, Product, Texts
from mongoengine import connect

random_bool = (True, False)


def random_string(str_length=10):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(str_length))


def seed_category(num_of_cats):
    category_list = []
    for i in range(num_of_cats):
        cat = Category(title=random_string()).save()
        category_list.append(cat)
    return category_list


def seed_products(num_of_products, *list_of_cats):
    for i in range(num_of_products):
        product = dict(
            title=random_string(),
            description=random_string(),
            price=random.randint(1000, 100 * 1000),
            quantity=random.randint(0, 100),
            is_available=random.choice(random_bool),
            is_discount=random.choice(random_bool),
            weight=random.uniform(0, 100),
            height=random.uniform(0, 100),
            width=random.uniform(0, 100),
            category=random.choice(list_of_cats)
        )
        Product(**product).save()


def seed_products_with_image():
    products = Product.objects.all()
    

    for i in products:
        with open('/Users/ezjust/itea_project/bot/images/test.png', 'rb') as image:
            i.image.replace(image)
            i.save()

    image.close()


if __name__ == '__main__':
    connect('bot_shop')
    seed_products_with_image()
    # text = dict(
    #     title='Greetings',
    #     text=random_string(500)
    # )
    # Texts(**text).save()
    #cats = seed_category(10)
    #seed_products(50, *cats)

    #Creating subcategories

    # cats = seed_category(3)
    # cat_obj = Category.objects.all().first()
    # cat_obj.sub_categories = cats
    # print(cat_obj.save())

