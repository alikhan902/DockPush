from rest_framework import serializers
from .models import Room
from .models import PlayerField


class PlayerFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerField
        fields = ['x', 'y', 'has_ship', 'is_shot', 'is_mis_shot']


class RoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = Room
        fields = ['id', 'name', 'turn', 'created_at']
        
        

class PlayerFieldUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerField
        fields = ['id', 'x', 'y', 'has_ship', 'is_shot', 'is_mis_shot']

    def update(self, instance, validated_data):
        """Обновление состояния клетки игрока."""
        instance.has_ship = validated_data.get('has_ship', instance.has_ship)
        instance.is_shot = validated_data.get('is_shot', instance.is_shot)
        instance.is_mis_shot = validated_data.get('is_mis_shot', instance.is_mis_shot)
        instance.save()
        return instance

class RoomSerializerOne(serializers.ModelSerializer):
    player_field = PlayerFieldSerializer(many=True)  # Поля для текущего игрока
    current_turn = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['id', 'name', 'turn', 'current_turn','player_field']   # Убираем opponent_field из полей

    def to_representation(self, instance):
        # Получаем сериализованные данные для игрока
        representation = super().to_representation(instance)

        # Получаем текущего пользователя (игрока, который делает запрос)
        current_user = self.context['request'].user

        # Получаем поля для игрока и противника
        if current_user == instance.user:
            # Текущий игрок - создатель комнаты
            player_fields = PlayerField.objects.filter(room=instance, player=instance.user)
            opponent_fields = PlayerField.objects.filter(room=instance, player=instance.opponent)
        elif current_user == instance.opponent:
            # Текущий игрок - противник
            player_fields = PlayerField.objects.filter(room=instance, player=instance.opponent)
            opponent_fields = PlayerField.objects.filter(room=instance, player=instance.user)
        else:
            # Если текущий пользователь не является ни одним из игроков (по ошибке)
            player_fields = []
            opponent_fields = []

        # Добавляем данные для полей игрока и противника
        representation['player_field'] = PlayerFieldSerializer(player_fields, many=True).data
        representation['opponent_field'] = PlayerFieldSerializer(opponent_fields, many=True).data

        return representation
    
    def get_current_turn(self, obj):
        """Метод для получения сообщения о текущем ходе"""
        current_user = self.context['request'].user

        if obj.turn % 2 == 1:
            if current_user == obj.user:
                return "Ваш ход"  # Ходит создатель комнаты
            else:
                return "Ход противника"  # Ход противника
        else:
            if current_user == obj.opponent:
                return "Ваш ход"  # Ходит противник
            else:
                return "Ход противка"  

