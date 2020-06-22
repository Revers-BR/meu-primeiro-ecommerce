from django.test import TestCase
from model_mommy import mommy
from checkout.models import CartItem, Order
from django.conf import settings

class CartItemTestCase(TestCase):
    """docstring for CartItemTestCase"""

    def setUp(self):
       mommy.make(CartItem, _quantity=3)

    def test_post_save_cart_item(self):
         
        cart_item = CartItem.objects.all()[0]
        cart_item.quantity = 0
        cart_item.save()
        self.assertEquals(CartItem.objects.count(), 2)

class OrderTestCase(TestCase):

    def setUp(self):

        self.cart_item = mommy.make(CartItem)
        self.user = mommy.make(settings.AUTH_USER_MODEL)

    def test_create_order(self):

        Order.order.create_order(self.user,[self.cart_item])
        self.assertEquals(Order.order.count(),1)
        order = Order.order.get()
        self.assertEquals(order.user, self.user)
        order_item = order.Items.get()
        self.assertEquals(order_item.product, self.cart_item.product)
