from django.core.management.base import BaseCommand, CommandError
from reservations.models import Performance, Seat


class Command(BaseCommand):
    help = (
        "공연별 좌석을 자동으로 생성합니다. "
        "기본은 A~J 열, 각 12석이며 이미 좌석이 있는 공연은 건너뜁니다."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--performance',
            type=int,
            help='특정 공연 ID만 생성하고 싶을 때 사용 (예: --performance 1)',
        )
        parser.add_argument(
            '--rows',
            type=str,
            default='ABCDEFGHIJ',
            help='좌석 열 문자들 (기본: ABCDEFGHIJ → A~J 10개 열)',
        )
        parser.add_argument(
            '--per-row',
            type=int,
            default=12,
            help='각 열당 좌석 개수 (기본: 12)',
        )

    def handle(self, *args, **options):
        perf_id = options.get('performance')
        rows_str = options.get('rows') or ''
        per_row = options.get('per_row') or 0

        if not rows_str:
            raise CommandError('rows 옵션이 비어 있습니다.')

        if per_row <= 0:
            raise CommandError('per-row 옵션은 1 이상이어야 합니다.')

        rows = list(rows_str)  # "ABC" → ["A", "B", "C"]

        # 대상 공연 목록 결정
        if perf_id:
            try:
                performances = [Performance.objects.get(pk=perf_id)]
            except Performance.DoesNotExist:
                raise CommandError(f'Performance(pk={perf_id}) 가 존재하지 않습니다.')
        else:
            performances = Performance.objects.all().order_by('start_at')

        if not performances:
            self.stdout.write(self.style.WARNING('생성할 공연이 없습니다.'))
            return

        total_created = 0

        for perf in performances:
            existing = Seat.objects.filter(performance=perf).count()
            if existing > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'[{perf.id}] "{perf}" 은(는) 이미 {existing}개 좌석이 있어 건너뜁니다.'
                    )
                )
                continue

            # 좌석 bulk 생성
            bulk = []
            for row in rows:
                for num in range(1, per_row + 1):
                    bulk.append(
                        Seat(
                            performance=perf,
                            row=row,
                            number=str(num),
                        )
                    )

            Seat.objects.bulk_create(bulk)
            created = len(bulk)
            total_created += created

            self.stdout.write(
                self.style.SUCCESS(
                    f'[{perf.id}] "{perf}" → {created}개 좌석 자동 생성 완료.'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(f'전체 생성 좌석 수: {total_created}개')
        )
