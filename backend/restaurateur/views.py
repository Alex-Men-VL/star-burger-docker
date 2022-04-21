from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from geopy import distance
from rest_framework.serializers import ModelSerializer

from coordinates.models import Coordinate
from foodcartapp.models import Order, Product, Restaurant, RestaurantMenuItem


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def get_order_distance(order_address, restaurant_address, coordinates):
    order_coordinates = list(
        filter(
            lambda order: (order['address'] == order_address),
            coordinates
        )
    )[0]
    restaurant_coordinates = list(
        filter(
            lambda restaurant: (
                restaurant['address'] == restaurant_address
            ),
            coordinates
        )
    )[0]
    if (not order_coordinates['are_defined']
            or not restaurant_coordinates['are_defined']):
        return None
    order_distance = distance.distance(
        (order_coordinates['lat'], order_coordinates['lon']),
        (restaurant_coordinates['lat'], restaurant_coordinates['lon'])
    )
    return order_distance.km


def serialize_order(order, restaurants, coordinates):
    suitable_restaurants = []
    for restaurant_id in order.suitable_restaurants_ids:
        restaurant_attrs = list(
            filter(
                lambda restaurant: (restaurant['id'] == restaurant_id),
                restaurants
            )
        )[0]
        order_distance = get_order_distance(order.address,
                                            restaurant_attrs['address'],
                                            coordinates)
        if order_distance:
            order_distance = f'{order_distance:.3f} км.'

        else:
            order_distance = 'неизвестно'
        suitable_restaurant = (restaurant_attrs["name"], order_distance)
        suitable_restaurants.append(suitable_restaurant)
    return {
        'id': order.id,
        'price': order.total_price,
        'name': f'{order.firstname} {order.lastname}',
        'address': order.address,
        'phonenumber': order.phonenumber,
        'comment': order.comment,
        'payment': order.get_payment_method_display(),
        'restaurants': suitable_restaurants
    }


def get_used_addresses(orders, restaurants):
    addresses = [order.address for order in orders]
    addresses += [restaurant['address'] for restaurant in restaurants]
    return addresses


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.filter(
        status=Order.UNPROCESSED
    ).fetch_with_price().fetch_with_suitable_restaurants()

    restaurants = Restaurant.objects.values('id', 'address', 'name')
    places_addresses = get_used_addresses(orders, restaurants)
    coordinates = Coordinate.objects.filter(
        address__in=places_addresses
    ).values('address', 'lat', 'lon', 'are_defined')
    context = {
        "order_items": [serialize_order(
            order,
            restaurants,
            coordinates
        ) for order in orders],
    }
    return render(request, template_name='order_items.html', context=context)
