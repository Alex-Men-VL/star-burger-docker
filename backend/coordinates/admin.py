from django.contrib import admin

from coordinates.models import Coordinate


@admin.register(Coordinate)
class CoordinateAdmin(admin.ModelAdmin):
    pass
