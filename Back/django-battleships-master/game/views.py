from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from .models import PlayerField, Room
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from .serializers import PlayerFieldSerializer, PlayerFieldUpdateSerializer, RoomSerializer, RoomSerializerOne
from .utils import delete_room, setup_fields_for_room
from django.contrib.auth.models import User

class CreateRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Создание комнаты (игры)"""
        name = request.data.get('name', 'GameRoom')  # Получаем имя комнаты из запроса
        opponent_username = request.data.get('opponent_username')  # Получаем имя пользователя противника

        # Проверка существования второго игрока
        try:
            opponent = User.objects.get(username=opponent_username)
        except User.DoesNotExist:
            return Response({"detail": "Игрок не найден"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        
        # Создаем комнату
        room = Room.objects.create(user=user, opponent=opponent, turn=1, name=name)

        # Инициализируем поля для обоих игроков
        setup_fields_for_room(room)

        # Возвращаем ответ с ID созданной комнаты
        return Response({"message": "Комната создана", "room_id": room.id}, status=status.HTTP_201_CREATED)

    def get_player_field(self, room):
        """Метод для получения данных поля игрока"""
        player_field = PlayerField.objects.filter(room=room)  # Получаем поле для игрока
        return PlayerFieldSerializer(player_field, many=True).data
    
    
class MyRoomsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Получение списка комнат пользователя"""
        # Получаем все комнаты, где текущий пользователь является владельцем или противником
        rooms = Room.objects.filter(user=request.user) | Room.objects.filter(opponent=request.user)

        # Сериализуем комнаты
        serializer = RoomSerializer(rooms, many=True)

        # Возвращаем список комнат
        return Response(serializer.data, status=status.HTTP_200_OK)

class RoomDetailAPIView(APIView):
    def get(self, request, id_room, *args, **kwargs):
        """Получение всех данных о комнате по ID"""
        try:
            room = Room.objects.get(id=id_room)
        except Room.DoesNotExist:
            raise NotFound(detail="Комната не найдена", code=status.HTTP_404_NOT_FOUND)

        # Сериализуем данные о комнате, передаем контекст (текущий пользователь)
        serializer = RoomSerializerOne(room, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateOpponentFieldAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, id_room, x, y, *args, **kwargs):
        """Обновление состояния клетки противника по координатам x и y"""
        try:
            room = Room.objects.get(id=id_room)
        except Room.DoesNotExist:
            raise NotFound(detail="Комната не найдена", code=status.HTTP_404_NOT_FOUND)

        # Получаем текущего пользователя
        current_user = request.user

        # Проверяем, чей сейчас ход
        if room.turn % 2 == 1:  # Нечетный ход - это первый игрок (создатель)
            if current_user != room.user:
                return Response({"detail": "Сейчас не ваш ход."}, status=status.HTTP_400_BAD_REQUEST)
        else:  # Четный ход - это второй игрок (противник)
            if current_user != room.opponent:
                return Response({"detail": "Сейчас не ваш ход."}, status=status.HTTP_400_BAD_REQUEST)

        # Ищем клетку противника
        # Если текущий пользователь - создатель комнаты, то мы проверяем поле второго игрока (противника)
        if current_user == room.user:
            opponent_field_instance = PlayerField.objects.filter(room=room, x=x, y=y, player=room.opponent).first()
        else:  # Если текущий пользователь - противник, то проверяем поле первого игрока
            opponent_field_instance = PlayerField.objects.filter(room=room, x=x, y=y, player=room.user).first()

        if not opponent_field_instance:
            return Response({"detail": "Клетка противника не найдена."}, status=status.HTTP_404_NOT_FOUND)

        # Сериализуем и обновляем клетку
        serializer = PlayerFieldUpdateSerializer(opponent_field_instance, data=request.data, partial=True)

        if serializer.is_valid():
            # Сохраняем изменения
            serializer.save()

            # Переключаем ход
            room.turn += 1
            room.save()

            return Response({
                "current_turn": room.turn,
                "turn": room.turn,
                "opponent_field": serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class DeleteRoomAPIView(APIView):
    def delete(self, request, id_room, *args, **kwargs):
        """Удаление комнаты по ID"""
        try:
            room = Room.objects.get(id=id_room)
        except Room.DoesNotExist:
            raise NotFound(detail="Комната не найдена", code=status.HTTP_404_NOT_FOUND)

        # Удаляем комнату
        room.delete()

        # Возвращаем успешный ответ о том, что комната была удалена
        return Response({"message": f"Room {id_room} deleted successfully."}, status=status.HTTP_200_OK)
