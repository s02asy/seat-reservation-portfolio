from django.contrib import admin
from .models import Performance, Seat, Reservation


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'start_at', 'end_at')
    list_filter = ('start_at',)


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('id', 'performance', 'row', 'number')
    list_filter = ('performance',)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'seat', 'user', 'status', 'created_at', 'expires_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'seat__performance__title')
