from mongoengine import *
from models.user_model import User


class Category(Document):
    title = StringField(max_length=64)
    sub_categories = ListField(ReferenceField('self'))


    @property
    def category_products(self):
        return Product.objects.filter(category=self, is_available=True)

    @property
    def is_parent(self):
        if self.sub_categories:
            return True

    def __str__(self):
        return f'{self.title}'


class Product(Document):
    title = StringField(max_length=64)
    image = FileField(required=True)
    description = StringField(max_length=1024)
    is_available = BooleanField()
    quantity = IntField(min_value=0)
    price = IntField(min_value=0)
    is_discount = BooleanField(default=False)
    category = ReferenceField(Category)
    weight = FloatField(min_value=0, null=True)
    width = FloatField(min_value=0, null=True)
    height = FloatField(min_value=0, null=True)

    def __str__(self):
        return f'name - {self.title}, category - {self.category},' \
               f' price - {self.price/100}'


class Texts(Document):
    title = StringField()
    text = StringField(max_length=2048)


    @classmethod
    def get_text(cls, title):
        return  cls.objects.filter(title=title).first().text


class Basket(Document):
    user = ReferenceField(User, required=True)
    products = ListField(ReferenceField(Product))
    is_archived = BooleanField(default=False)

    @property
    def get_sum(self):
        basket_sum = 0
        for p in self.products:
            basket_sum += p.price

        return basket_sum/100

    @classmethod
    def create_append_to_basket(cls, product_id, user_id):
        user = User.objects.get(user_id=user_id)
        user_basket = cls.objects.filter(user=user).first()
        product = Product.objects.get(id=product_id)

        if user_basket and not user_basket.is_archived:
            user_basket.products.append(product)
            user_basket.save()
        else:
            cls(user=user, products=[product]).save()

    def clean_basket(self):
        self.products = []
        self.save()


class OrdersHistory(Document):
    user = ReferenceField(User)
    orders = ListField(ReferenceField(Basket))

    @classmethod
    def get_or_create(cls, user):
        history = cls.objects.filter(user=user)
        if history:
            return history
        else:
            return cls(user).save()




