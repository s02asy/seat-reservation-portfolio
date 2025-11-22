import re
from django import forms
from .models import User

# 영문 소문자 + 숫자만 허용
USERNAME_REGEX = re.compile(r'^[a-z0-9]+$')

class SignupForm(forms.ModelForm):
    password1 = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput,
        strip=False,
    )
    password2 = forms.CharField(
        label='비밀번호 확인',
        widget=forms.PasswordInput,
        strip=False,
    )

    class Meta:
        model = User
        fields = ['username', 'real_name', 'phone_number']
        labels = {
            'username': '아이디',
            'real_name': '이름',
            'phone_number': '휴대폰 번호',
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('비밀번호가 서로 일치하지 않습니다.')
        return p2

    def save(self, commit=True):
        """
        비밀번호를 평문으로 저장하지 않고,
        Django가 제공하는 안전한 해시(set_password)로 저장.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])

        # 지금은 PASS 인증 연동 전이므로 예시로 is_verified=True 를 줍니다.
        # 나중에 PASS 콜백에서만 True 로 변경하도록 수정 가능.
        user.is_verified = True

        if commit:
            user.save()
        return user
    
    def clean_username(self):
        username = (self.cleaned_data.get('username') or '').strip()

        if not username:
            raise forms.ValidationError('아이디를 입력해 주세요.')
        
        # 🔽 모든 아이디를 소문자로 통일
        username = username.lower()

        # ✅ 영문/숫자만 허용 (한글, 특수문자, 공백 전부 불가)
        if not USERNAME_REGEX.match(username):
            raise forms.ValidationError('아이디는 영문과 숫자만 사용할 수 있습니다.')

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('이미 사용 중인 아이디입니다.')

        return username