from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .forms import UserForm

class SignupAPIView(APIView):

    def post(self, request, *args, **kwargs):
        user_form = UserForm(data=request.data)


        # Проверяем, прошли ли формы валидацию
        if user_form.is_valid():
            # Сохраняем пользователя
            user = user_form.save()
            user.set_password(user.password)  # Шифруем пароль
            user.save()

            # Аутентификация пользователя
            user = authenticate(
                username=user_form.cleaned_data['username'],
                password=user_form.cleaned_data['password']
            )

            if user is not None:
                login(request, user)
                return Response({'message': 'Пользователь зарегистрирован'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Ошибка регистрации'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Получаем ошибки формы
            user_form_errors = self.extract_error_messages(user_form.errors)


            print(user_form_errors)
            return Response(user_form_errors, status=status.HTTP_400_BAD_REQUEST)
    
    def extract_error_messages(self, form_errors):
        """
        Извлекает только сообщения об ошибках из формы и возвращает их в виде словаря.
        """
        error_messages = {}
        for field, error_list in form_errors.items():
            if error_list:  # Если список ошибок не пуст
                # Возвращаем только первое сообщение об ошибке для каждого поля
                error_messages[field] = error_list[0].message if hasattr(error_list[0], 'message') else error_list[0]
        return error_messages


class LoginAPIView(APIView):

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                return Response({'message': 'Успешная авторизация'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Ваша учетная запись отключена'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'message': 'Неверный пароль или логин'}, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({'message': 'Вы вышли из аккаунта'}, status=status.HTTP_200_OK)
