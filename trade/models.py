from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('trader', 'Trader'),
        ('admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(choices=ROLE_CHOICES, max_length=50, default='trader')

    def __str__(self):
        return f"{self.user.username} ({self.role})"

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_or_update_userprofile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()

class Order(models.Model):
    BUY = 'buy'
    SELL = 'sell'
    ORDER_TYPE_CHOICES = [(BUY, 'Buy'), (SELL, 'Sell')]
    MARKET = 'market'
    LIMIT = 'limit'
    STATUS_ACTIVE = 'active'
    STATUS_BOUGHT = 'bought'
    STATUS_SOLD = 'sold'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_BOUGHT, 'Bought'),
        (STATUS_SOLD, 'Sold'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]
    ORDER_STYLE_CHOICES = [(MARKET, 'Market'), (LIMIT, 'Limit')]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_type = models.CharField(choices=ORDER_TYPE_CHOICES, max_length=20)
    order_style = models.CharField(choices=ORDER_STYLE_CHOICES, max_length=20, default=LIMIT)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    quantity = models.PositiveIntegerField()
    quantity_filled = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def remaining_quantity(self):
        return self.quantity - self.quantity_filled

    def __str__(self):
        return f"{self.user.username} {self.order_type} {self.quantity} @ {self.price} {self.status}"

class Trade(models.Model):
    buy_order = models.ForeignKey(Order, related_name="buy_trades", on_delete=models.CASCADE)
    sell_order = models.ForeignKey(Order, related_name="sell_trades", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trade {self.quantity} @ {self.price}"

