# accounts/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class CaseInsensitiveModelBackend(ModelBackend):
    """
    username 을 대소문자 구분 없이 인증하는 백엔드
    - 로그인 시 입력 값은 lower() 해서 username__iexact 로 검색
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return None

        username = username.strip().lower()   # ✅ 입력 아이디 소문자로 통일

        try:
            user = UserModel.objects.get(**{f'{UserModel.USERNAME_FIELD}__iexact': username})
        except UserModel.DoesNotExist:
            # 타이밍 공격 방지용 dummy
            UserModel().set_password(password)
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None
