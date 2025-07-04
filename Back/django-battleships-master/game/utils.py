from .models import PlayerField
import random

def is_area_clear(field, x, y, length, direction):
    """Проверка, свободна ли область вокруг корабля"""
    # Для проверки свободности клеток вокруг корабля
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1), (1, 0), (1, 1)
    ]
    
    # Проверяем координаты вокруг корабля
    for i in range(length):
        # Если корабль горизонтальный, проверяем клетки вокруг каждой клетки на оси X
        if direction == 0:
            check_x, check_y = x + i, y
        # Если корабль вертикальный, проверяем клетки вокруг каждой клетки на оси Y
        else:
            check_x, check_y = x, y + i
        
        for dx, dy in directions:
            check_coord_x, check_coord_y = check_x + dx, check_y + dy
            if 0 <= check_coord_x < 10 and 0 <= check_coord_y < 10:
                # Если клетка занята, возвращаем False
                if field.filter(x=check_coord_x, y=check_coord_y, has_ship=True).exists():
                    return False
    return True


def generate_ships_for_field(field):
    """Генерация кораблей на поле с длиной 4, 3 и 2"""
    ships = [
        {'length': 4, 'count': 1},  # Один корабль длиной 4
        {'length': 3, 'count': 2},  # Два корабля длиной 3
        {'length': 2, 'count': 3}   # Три корабля длиной 2
    ]

    placed_ships = set()  # Для отслеживания занятых клеток

    def place_ship(length):
        """Функция для размещения одного корабля"""
        while True:
            # Случайно выбираем направление: 0 - горизонтально, 1 - вертикально
            direction = random.choice([0, 1])

            # Случайно выбираем начальные координаты (x, y)
            if direction == 0:  # Горизонтально
                x = random.randint(0, 9 - length)  # Ограничение для горизонтального размещения
                y = random.randint(0, 9)
            else:  # Вертикально
                x = random.randint(0, 9)
                y = random.randint(0, 9 - length)  # Ограничение для вертикального размещения

            # Проверяем, можно ли разместить корабль (проверка на занятые клетки и соприкосновения)
            if is_area_clear(field, x, y, length, direction):
                coordinates = set((x + i, y) if direction == 0 else (x, y + i) for i in range(length))

                # Если все клетки свободны, размещаем корабль
                for coord in coordinates:
                    placed_ships.add(coord)
                    field_object = field.filter(x=coord[0], y=coord[1]).first()  # Находим клетку
                    if field_object:
                        field_object.has_ship = True
                        field_object.save()
                break  # Корабль размещен, выходим из цикла

    # Размещаем корабли согласно заданному количеству и длине
    for ship in ships:
        for _ in range(ship['count']):
            place_ship(ship['length'])
            
def setup_fields_for_room(room):
    """Настройка полей для двух игроков"""
    for x in range(10):
        for y in range(10):
            # Для первого игрока (создатель комнаты)
            PlayerField.objects.create(room=room, x=x, y=y, has_ship=False, is_shot=False, player=room.user)

            # Для второго игрока (противник)
            PlayerField.objects.create(room=room, x=x, y=y, has_ship=False, is_shot=False, player=room.opponent)

    # Генерация кораблей для обоих игроков
    generate_ships_for_field(PlayerField.objects.filter(room=room, player=room.user))  # Генерация кораблей для первого игрока
    generate_ships_for_field(PlayerField.objects.filter(room=room, player=room.opponent))  # Генерация кораблей для второго игрока


def delete_room(room):
    """Удаление комнаты после завершения игры"""
    room.delete()
    print(f"Room {room.id} deleted after game over.")
