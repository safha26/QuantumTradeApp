from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegistrationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from .order_matching import *
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db import IntegrityError
from .decorators import role_required
from django.views.decorators.http import require_GET
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from .serializers import OrderSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods




# Create your views here.
def dashboard(request):
    buy_orders = Order.objects.filter(order_type='buy', status='active').order_by('-price', 'created_at')
    sell_orders = Order.objects.filter(order_type='sell', status='active').order_by('price', 'created_at')
    trades = Trade.objects.all().order_by('-timestamp')
    return render(request, 'trade/dashboard.html', {
        'buy_orders': buy_orders,
        'sell_orders': sell_orders,
        'trades': trades,
    })


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Registration successful. Please login.")
                return redirect('login')  # Update 'login' to your login URL name
            except Exception as e:
                form.add_error(None, f"An unexpected error occurred: {str(e)}")
    else:
        form = UserRegistrationForm()
    return render(request, 'trade/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'trade/login.html')

@login_required
@require_http_methods(["GET", "POST"])
def place_order(request):
    if request.method == 'GET':
        return render(request, 'trade/place_order.html')
    elif request.method == 'POST':
        # Process the order on POST requests
        quantity_str = request.POST.get('quantity')
        order_type = request.POST.get('order_type')
        order_style = request.POST.get('order_style', 'limit')
        price = request.POST.get('price')

        # Validation for quantity
        try:
            quantity = int(quantity_str)
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid quantity'}, status=400)

        if order_style == 'market':
            price = None

        try:
            Order.objects.create(
                user=request.user,
                order_type=order_type,
                order_style=order_style,
                price=price,
                quantity=quantity,
            )
            match_orders()
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        return JsonResponse({'success': 'Order placed successfully'})

@login_required
def cancel_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user, status='active')
        order.status = 'canceled'
        order.save()
        messages.success(request, "Order canceled successfully")
    except Order.DoesNotExist:
        messages.error(request, "Order does not exist")
    return redirect('dashboard')


def logout_view(request):
    logout(request)
    return redirect('login')

@swagger_auto_schema(method='get', responses={200: OrderSerializer(many=True)})
@api_view(['GET', 'POST'])
def order_book_api(request):
    buy_orders = Order.objects.filter(order_type='buy', status='active')
    serializer = OrderSerializer(buy_orders, many=True)
    return Response(serializer.data)

@require_GET
def trade_history_api(request):
    try:
        trades = list(Trade.objects.all().order_by('-timestamp').values('price', 'quantity', 'timestamp')[:30])
        return JsonResponse({'trades': trades})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status = 500)

@login_required
def your_dashboard(request):
    user_buy_orders = Order.objects.filter(user=request.user, order_type = 'buy', status='active').order_by('price', '-created_at')
    user_sell_orders = Order.objects.filter(user=request.user, order_type='sell', status='active')
    user_trades = Trade.objects.filter(
        buy_order__user=request.user).union(Trade.objects.filter(sell_order__user=request.user).order_by('-timestamp')
    )
    active_orders = request.user.order_set.filter(status='active')
    return render(request, 'trade/your_dashboard.html', {
        'active_orders': active_orders,
        'user_buy_orders': user_buy_orders,
        'user_sell_orders': user_sell_orders,
        'user_trades': user_trades,})
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
@role_required('admin')
def manage_users(request):
    users = User.objects.all().select_related('userprofile')

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_role = request.POST.get('role')

        try:
            user = User.objects.get(id=user_id)
            user.userprofile.role = new_role
            user.userprofile.save()
            messages.success(request, f"Role updated for user {user.username}")
        except User.DoesNotExist:
            messages.error(request, "User does not exist")
        return redirect('manage_users')

    return render(request, 'trade/manage_users.html', {'users': users})

class OrderSerializer(serializers.Serializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField()
