from django.db import models
from django.utils import timezone


class Coordinate(models.Model):
    address = models.CharField(
        'адрес',
        max_length=100,
        unique=True
    )
    lon = models.FloatField(
        'долгота',
        null=True,
        blank=True,
    )
    lat = models.FloatField(
        'широта',
        null=True,
        blank=True,
    )
    are_defined = models.BooleanField(
        'координаты определены',
        default=False
    )
    request_date = models.DateTimeField(
        'дата запроса к геокодеру',
        default=timezone.now
    )

    class Meta:
        verbose_name = 'координаты'
        verbose_name_plural = 'координаты'

    def __str__(self):
        return f'{self.address} ({self.lon} {self.lat})'
