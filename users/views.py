from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # 입력: username(표시명), id(로그인ID), password, password_confirm
        username_display = request.data.get('username')
        login_id = request.data.get('id')
        pw = request.data.get('password')
        pw2 = request.data.get('password_confirm')

        if not all([username_display, login_id, pw, pw2]):
            return Response({"detail": "필수 필드 누락"}, status=400)
        if pw != pw2:
            return Response({"detail": "비밀번호가 일치하지 않습니다."}, status=400)
        if User.objects.filter(username=login_id).exists():
            return Response({"detail": "이미 사용 중인 ID입니다."}, status=409)

        user = User.objects.create_user(username=login_id, password=pw, first_name=username_display)
        return Response({"user_id": user.id, "username": user.first_name, "id": user.username}, status=201)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        login_id = request.data.get('id')
        pw = request.data.get('password')
        user = authenticate(request, username=login_id, password=pw)
        if user is None:
            return Response({"detail": "ID 혹은 비밀번호가 올바르지 않습니다."}, status=401)
        login(request, user)  # Django 세션 생성 → sessionid 쿠키 발급
        return Response({"user_id": user.id, "username": user.first_name, "id": user.username}, status=200)


class LogoutView(APIView):
    def post(self, request):
        logout(request)  # 세션 종료
        return Response(status=204)


class MeView(APIView):
    def get(self, request):
        u = request.user
        return Response({"user_id": u.id, "username": u.first_name, "id": u.username}, status=200)