from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import IntegerField
from django.db.models.functions import Cast
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from .models import Performance, Seat, Reservation
from django.db.models import Count, Q


@login_required
def performance_list(request):
    """공연 목록 + 좌석 잔여 수 요약"""
    now = timezone.now()

    performances = (
        Performance.objects
        .annotate(
            # 공연별 전체 좌석 수
            total_seats=Count('seats', distinct=True),

            # 확정된 좌석 수 (CONFIRMED)
            confirmed_seats=Count(
                'seats',
                filter=Q(seats__reservation__status=Reservation.STATUS_CONFIRMED),
                distinct=True,
            ),

            # ✨ 아직 만료되지 않은 HOLD 좌석 수만 카운트
            hold_seats=Count(
                'seats',
                filter=Q(
                    seats__reservation__status=Reservation.STATUS_HOLD,
                    seats__reservation__expires_at__gt=now,  # 만료 시간 > 현재
                ),
                distinct=True,
            ),
        )
        .order_by('start_at')
    )

    # 파이썬에서 잔여 좌석 계산:
    #   잔여 = 전체 - (확정 + 유효한 HOLD)
    for perf in performances:
        perf.available_seats = (
            perf.total_seats - perf.confirmed_seats - perf.hold_seats
        )

    return render(
        request,
        'reservations/performance_list.html',
        {
            'performances': performances,
            'now': now,
        },
    )

@login_required
def seat_map(request, performance_id: int):
    performance = get_object_or_404(Performance, pk=performance_id)

    seats = (
        Seat.objects
        .filter(performance=performance)
        .select_related('reservation')
        # number(문자열)를 정수로 캐스팅해서 정렬용 컬럼 추가
        .annotate(number_int=Cast('number', IntegerField()))
        .order_by('row', 'number_int')   # 행 → 숫자 순으로 정렬
    )

    return render(request, 'reservations/seat_map.html', {
        'performance': performance,
        'seats': seats,
    })

@login_required
@transaction.atomic
def reserve_seat(request, performance_id: int, seat_id: int):
    """
    좌석 예약 API (임시홀드)
    - 반드시 POST만 허용
    - select_for_update() 로 좌석 행 잠금
    - 이미 예약된 좌석이면 에러
    - 만료된 HOLD는 CANCEL 처리 후 다시 예약 허용
    """

    # 🔐 본인인증 여부 체크 (개발 중에는 잠깐 주석 처리해도 됩니다)
    if not request.user.is_verified:
        return JsonResponse(
            {'ok': False, 'message': '본인인증 완료된 계정만 예약할 수 있습니다.'},
            status=403
        )

    if request.method != 'POST':
        return HttpResponseBadRequest('POST 요청만 허용됩니다.')

    # 공연 검증
    performance = get_object_or_404(Performance, pk=performance_id)

    # 동시성 제어: Seat 행만 FOR UPDATE로 잠금 (JOIN 금지)
    seat = (
        Seat.objects
        .select_for_update()
        .get(pk=seat_id, performance=performance)
    )

    now = timezone.now()

    # 이 좌석에 이미 연결된 예약(있을 수도 있고 없을 수도 있음)
    try:
        existing = seat.reservation   # OneToOne 역참조
    except Reservation.DoesNotExist:
        existing = None

    if existing:
        # 1) 만료된 HOLD 인 경우 → CANCEL로 바꾸고 재사용 가능
        if (
            existing.status == Reservation.STATUS_HOLD and
            existing.expires_at is not None and
            existing.expires_at < now
        ):
            existing.status = Reservation.STATUS_CANCELLED
            existing.save(update_fields=['status'])

        # 2) 아직 유효한 HOLD 또는 확정 예약이면 → 재예약 불가
        elif existing.status in (
            Reservation.STATUS_HOLD,
            Reservation.STATUS_CONFIRMED,
        ):
            return JsonResponse(
                {'ok': False, 'message': '이미 예약된 좌석입니다.'},
                status=400
            )
        # 3) STATUS_CANCELLED 는 그냥 새로 홀드로 덮어쓸 것임 (update_or_create)

    # 새 임시 홀드 만료 시각 (예: 1분)
    expires_at = now + timezone.timedelta(minutes=1)

    # 기존 row가 있으면 update, 없으면 create (OneToOne 충돌 방지)
    reservation, created = Reservation.objects.update_or_create(
        seat=seat,
        defaults={
            'user': request.user,
            'status': Reservation.STATUS_HOLD,
            'expires_at': expires_at,
        }
    )

    # ✅ WebSocket 브로드캐스트: 이 공연 방에 좌석 상태 변경 알림
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"performance_{performance.id}",
        {
            "type": "seat_status",           # consumers.SeatConsumer.seat_status 메서드를 호출
            "seat_id": seat.id,
            "status": reservation.status,    # 'HOLD' / 나중에 'CONFIRMED' 등
            "expires_at": expires_at.isoformat(),
        }
    )

    return JsonResponse({
        'ok': True,
        'reservation_id': reservation.id,
        'expires_at': expires_at.isoformat(),
    })