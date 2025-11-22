"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    # 루트 접속시 로그인 페이지로 리다이렉트
    path('', lambda request: redirect('accounts:login'), name='root'),
    path('admin/', admin.site.urls),
    # 우리 회원가입/기타 계정용 URL
    path('accounts/', include('accounts.urls')),
    # 로그인/로그아웃 (장고 기본 뷰 사용)
    path('accounts/', include('django.contrib.auth.urls')),
    # 좌석 예약 앱
    path('reservations/', include('reservations.urls')),
]
