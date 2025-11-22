from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    path('', views.performance_list, name='performance_list'),
    path('performance/<int:performance_id>/seats/', views.seat_map, name='seat_map'),
    path(
        'performance/<int:performance_id>/seats/<int:seat_id>/reserve/',
        views.reserve_seat,
        name='reserve_seat'
    ),
]