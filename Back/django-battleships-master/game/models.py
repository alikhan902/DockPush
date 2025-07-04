from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='creator')  # Игрок, создавший комнату
    opponent = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='opponent')  # Второй игрок
    created_at = models.DateTimeField(auto_now_add=True)  # Когда комната была создана
    name = models.CharField(max_length=20, default="GameRoom")  # Имя комнаты
    turn = models.IntegerField(default=0)  # Счетчик ходов (по сути, также чье сейчас ход)
    is_game_over = models.BooleanField(default=False)  # Завершена ли игра

    def __str__(self):
        return f"Room {self.id} - Player: {self.user.username} - {self.name}"


class PlayerField(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='player_field')
    player = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # Устанавливаем значение по умолчанию для player
    x = models.IntegerField()
    y = models.IntegerField()
    has_ship = models.BooleanField(default=False)
    is_shot = models.BooleanField(default=False)
    is_mis_shot = models.BooleanField(default=False)

    def __str__(self):
        return f"PlayerField for Room {self.room.id} - Player {self.player.username} - Cell ({self.x}, {self.y})"
