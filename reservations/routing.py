from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path(
        "ws/reservations/performance/<int:performance_id>/",
        consumers.SeatConsumer.as_asgi(),
        name="seat_ws",
    ),
]
