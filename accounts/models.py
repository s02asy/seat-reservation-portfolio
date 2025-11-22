from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    기본 Django User에 실명인증용 필드를 몇 개 더 얹은 모델
    - username / password / email 등 기본 필드는 AbstractUser에서 상속
    """

    # PASS / 본인인증에서 내려오는 식별값 (CI/DI 같은 것)
    identity_key = models.CharField(
        max_length=128,
        unique=True,
        null=True,
        blank=True,
        help_text='본인인증 기관에서 내려주는 사용자 고유 식별값'
    )

    # 실명 / 휴대폰번호 (실제 서비스면 최소 수집 원칙에 맞춰 관리)
    real_name = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    # 본인인증 완료 여부 + 마지막 인증 시각
    is_verified = models.BooleanField(default=False)
    last_verified_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        # admin 화면 등에서 보기 편하게
        if self.real_name:
            return f'{self.username} ({self.real_name})'
        return self.username