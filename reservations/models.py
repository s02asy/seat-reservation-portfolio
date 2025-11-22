from django.db import models
from django.conf import settings
from django.utils import timezone


class Performance(models.Model):
    """공연/상영 회차 같은 개념"""
    title = models.CharField(max_length=200)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    def __str__(self):
        return f'{self.title} ({self.start_at:%Y-%m-%d %H:%M})'


class Seat(models.Model):
    """공연별 좌석"""
    performance = models.ForeignKey(
        Performance,
        on_delete=models.CASCADE,
        related_name='seats'
    )
    row = models.CharField(max_length=5)
    number = models.CharField(max_length=5)

    class Meta:
        unique_together = ('performance', 'row', 'number')

    def __str__(self):
        return f'{self.performance.title} - {self.row}{self.number}'


class Reservation(models.Model):
    """좌석 예약(홀드/확정/취소 상태 포함)"""
    STATUS_HOLD = 'HOLD'
    STATUS_CONFIRMED = 'CONFIRMED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_HOLD, '임시홀드'),
        (STATUS_CONFIRMED, '확정'),
        (STATUS_CANCELLED, '취소'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    seat = models.OneToOneField(
        Seat,
        on_delete=models.PROTECT,
        related_name='reservation'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_HOLD,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
        ]

    def is_expired(self) -> bool:
        """임시홀드 만료 여부"""
        return (
            self.status == self.STATUS_HOLD
            and self.expires_at is not None
            and self.expires_at < timezone.now()
        )

    def __str__(self):
        return f'{self.seat} - {self.user} ({self.status})'
