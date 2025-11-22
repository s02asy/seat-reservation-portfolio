from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth import get_user_model
from .forms import USERNAME_REGEX

from .forms import SignupForm

User = get_user_model()


def signup_view(request):
    """
    회원가입:
    - 계정만 생성하고
    - 로그인은 사용자가 /accounts/login/ 에서 직접 하도록
    """
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()           # ← user = form.save() 만 하고
            return redirect('login')  # 로그인 페이지로 이동
    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})

@require_GET
def check_username(request):
    username = (request.GET.get('username') or '').strip()
    if not username:
        return JsonResponse({'ok': False, 'message': '아이디를 입력해 주세요.'}, status=400)

    username_lower = username.lower()

    # 규칙 위반(한글/특수문자 등) → 프론트에서 별도 처리
    if not USERNAME_REGEX.match(username_lower):
        return JsonResponse({
            'ok': True,
            'exists': False,
            'invalid': True,
            'message': '아이디는 영문과 숫자만 사용할 수 있습니다.',
        })

    exists = User.objects.filter(username__iexact=username_lower).exists()
    return JsonResponse({'ok': True, 'exists': exists})