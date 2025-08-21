from django.db import transaction
from .models import Order, Trade
from .serializers import OrderSerializer, TradeSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import render


@transaction.atomic
def match_orders():

    buy_orders = Order.objects.filter(order_type='buy', status='active').order_by('-price', 'created_at')
    sell_orders = Order.objects.filter(order_type='sell', status='active').order_by('price', 'created_at')

    for buy_order in buy_orders:
        if buy_order.remaining_quantity <= 0:
            continue

        # Filter potential sell orders for this buy order
        potential_sells = sell_orders.filter(status='active')

        if buy_order.order_style == 'limit' and buy_order.price is not None:
            potential_sells = potential_sells.filter(price__lte=buy_order.price)

        for sell_order in potential_sells:
            if sell_order.remaining_quantity <= 0:
                continue

            # Skip if prices incompatible for limit orders
            if sell_order.order_style == 'limit' and buy_order.order_style == 'limit':
                if sell_order.price is not None and buy_order.price is not None:
                    if sell_order.price > buy_order.price:
                        continue

            trade_qty = min(buy_order.remaining_quantity, sell_order.remaining_quantity)

            # Determine trade price
            if buy_order.order_style == 'market' and sell_order.order_style == 'limit':
                trade_price = sell_order.price
            elif buy_order.order_style == 'limit' and sell_order.order_style == 'market':
                trade_price = buy_order.price
            elif buy_order.order_style == 'market' and sell_order.order_style == 'market':
                trade_price = 0  # or last known price if tracked separately
            else:
                trade_price = buy_order.price

            # Create Trade
            Trade.objects.create(
                buy_order=buy_order,
                sell_order=sell_order,
                price=trade_price,
                quantity=trade_qty,
            )

            # Update orders filled quantities
            buy_order.quantity_filled += trade_qty
            sell_order.quantity_filled += trade_qty

            # Update status accordingly
            buy_order.status = Order.STATUS_BOUGHT if buy_order.remaining_quantity <= 0 else Order.STATUS_ACTIVE
            sell_order.status = Order.STATUS_SOLD if sell_order.remaining_quantity <= 0 else Order.STATUS_ACTIVE

            buy_order.save()
            sell_order.save()

            # Send real-time update notification after saving orders
            send_orderbook_update()

            if buy_order.remaining_quantity <= 0:
                break  # Move to next buy_order

def send_orderbook_update():
    channel_layer = get_channel_layer()

    buy_orders = Order.objects.filter(order_type='buy', status='active')
    sell_orders = Order.objects.filter(order_type='sell', status='active')
    recent_trades = Trade.objects.all().order_by('-timestamp')[:15]

    data = {
        "buy_orders": OrderSerializer(buy_orders, many=True).data,
        "sell_orders": OrderSerializer(sell_orders, many=True).data,
        "recent_trades": TradeSerializer(recent_trades, many=True).data,
        "trade_completed": True,  # Flag to trigger notification
    }

    async_to_sync(channel_layer.group_send)(
        "orderbook",
        {
            "type": "order_book_update",
            "data": data,
        }
    )

    # return render(request, 'trade/your_dashboard.html', {
    #     'recent_trades': recent_trades,})

