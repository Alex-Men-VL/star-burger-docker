from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):

    def fetch_with_price(self):
        orders_with_price = self.annotate(
            total_price=Sum('order_items__price')
        )
        return orders_with_price

    def fetch_with_suitable_restaurants(self):
        orders = self.prefetch_related('products').order_by('-pk')
        orders_products_ids = orders.values_list('products', flat=True)
        restaurant_menu_items = RestaurantMenuItem.objects.filter(
            product__in=orders_products_ids, availability=True
        ).values_list(
            'product',
            'restaurant'
        )
        product_for_restaurants = {}
        for product_id, restaurant_id in restaurant_menu_items:
            product_for_restaurants.setdefault(product_id, []).append(
                restaurant_id
            )
        for order in orders:
            products = order.products.all()
            suitable_restaurants_ids = product_for_restaurants[products[0].id]

            for product in products[1:]:
                suitable_restaurants_ids = list(
                    set(suitable_restaurants_ids)
                    & set(product_for_restaurants[product.id])
                )
            order.suitable_restaurants_ids = suitable_restaurants_ids
        return orders


class Order(models.Model):
    UNPROCESSED = 'NP'
    PROCESSED = 'P'
    DELIVERED = 'D'
    ORDER_STATUS_CHOICE = [
        (UNPROCESSED, 'не обработан'),
        (PROCESSED, 'обработан'),
        (DELIVERED, 'доставлен'),
    ]

    IN_CASH = 'CH'
    BY_CARD = 'CD'
    NOT_SPECIFIED = 'NS'
    PAYMENT_METHOD_CHOICE = [
        (IN_CASH, 'Наличностью'),
        (BY_CARD, 'Электронно'),
        (NOT_SPECIFIED, 'Не указано')
    ]

    address = models.CharField(
        'адрес',
        max_length=100
    )
    firstname = models.CharField(
        'имя заказчика',
        max_length=20
    )
    lastname = models.CharField(
        'фамилия заказчика',
        max_length=20
    )
    phonenumber = PhoneNumberField(
        'контактный телефон',
        db_index=True
    )
    products = models.ManyToManyField(
        Product,
        related_name='orders',
        verbose_name='товары',
        through='OrderItem',
    )
    status = models.CharField(
        'статус заказа',
        max_length=12,
        choices=ORDER_STATUS_CHOICE,
        default=UNPROCESSED,
        db_index=True,
    )
    comment = models.TextField(
        'комментарий',
        default='',
        blank=True
    )
    payment_method = models.CharField(
        'способ оплаты',
        max_length=12,
        choices=PAYMENT_METHOD_CHOICE,
        default=NOT_SPECIFIED,
        db_index=True,
    )
    registered_at = models.DateTimeField(
        'дата оформления',
        default=timezone.now,
        db_index=True
    )
    called_at = models.DateTimeField(
        'дата звонка',
        null=True,
        blank=True,
        db_index=True
    )
    delivered_at = models.DateTimeField(
        'дата доставки',
        null=True,
        blank=True,
        db_index=True
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.address}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name='заказ',
        related_name='order_items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='товар',
        related_name='order_items'
    )
    quantity = models.IntegerField(
        'количество',
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        'стоимость позиции с учетом количества',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return f'{self.product.name} {self.order.firstname} ' \
               f'{self.order.lastname} {self.order.address}'
