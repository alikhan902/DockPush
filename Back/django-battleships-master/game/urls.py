from django.urls import path 
from .views import CreateRoomAPIView, DeleteRoomAPIView, MyRoomsAPIView, RoomDetailAPIView, UpdateOpponentFieldAPIView

urlpatterns = [
    path('create_room/', CreateRoomAPIView.as_view(), name='create_room'),  # Создание комнаты
    path('my_rooms/', MyRoomsAPIView.as_view(), name='my_rooms'),  # Получение списка комнат пользователя
    path('my_room/<int:id_room>/', RoomDetailAPIView.as_view(), name='room_detail'),
    path('my_room/<int:id_room>/update/<int:x>/<int:y>/', UpdateOpponentFieldAPIView.as_view(), name='update_field'),
    path('my_room/<int:id_room>/delete/', DeleteRoomAPIView.as_view(), name='delete_room'),
]
