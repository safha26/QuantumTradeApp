from django.test import TestCase
from django.contrib.auth.models import User
from .models import Order, Trade
from .order_matching import match_orders

# Create your tests here.

class OrderTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username = 'buyer', password = 'pass123')
        self.user2 = User.objects.create_user(username = 'seller', password = 'pass123')
    def test_order_creation(self):
        order = Order.objects.create(user = self.user1, order_type = 'buy', order_style = 'limit', price = 100, quantity = 5)
        self.assertEqual(order.status, 'active')

    def test_order_matching_creates_trade(self):
        buy_order = Order.objects.create(user=self.user1, order_type = 'buy', order_style = 'limit', price = 100, quantity = 5)
        sell_order = Order.objects.create(user=self.user2, order_type = 'sell', order_style = 'limit', price = 100, quantity = 5)
        match_orders()
        trade = Trade.objects.filter(buy_order=buy_order, sell_order=sell_order).first()
        self.assertIsNotNone(trade)
        self.assertEqual(trade.price, sell_order.price)
    class ViewTests(TestCase):
        def test_place_order_view_redirects_if_not_logged_in(self):
            response = self.client.get('/place_order/')
            self.assertRedirects(response, '/login/?next=/place_order/')

