"""
API Serializers для REST API.
"""
from rest_framework import serializers
from core.models import User
from mlm.models import StructureNode, Tariff
from billing.models import Payment, Bonus


class TariffSerializer(serializers.ModelSerializer):
    """Сериализатор для тарифа."""
    
    class Meta:
        model = Tariff
        fields = ['code', 'name', 'entry_amount', 'green_bonus_percent', 'yellow_bonus_percent']


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'status', 'referral_code', 'invited_by', 'date_joined']
        read_only_fields = ['id', 'referral_code', 'date_joined']


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для платежа."""
    tariff = TariffSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'user', 'tariff', 'amount', 'status', 'created_at', 'completed_at']
        read_only_fields = ['id', 'created_at', 'completed_at']


class QueueItemSerializer(serializers.Serializer):
    """Сериализатор для элемента очереди регистраций."""
    id = serializers.IntegerField()
    user = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    inviter = serializers.CharField(allow_null=True)
    inviter_username = serializers.CharField(allow_null=True)
    tariff = TariffSerializer()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    created_at = serializers.DateTimeField()


class StructureNodeSerializer(serializers.ModelSerializer):
    """Сериализатор для узла структуры."""
    user = UserSerializer(read_only=True)
    parent_username = serializers.CharField(source='parent.username', read_only=True, allow_null=True)
    tariff_name = serializers.CharField(source='tariff.name', read_only=True, allow_null=True)
    tariff_code = serializers.CharField(source='tariff.code', read_only=True, allow_null=True)
    
    class Meta:
        model = StructureNode
        fields = [
            'id', 'user', 'parent_username', 'level', 'position', 
            'tariff_name', 'tariff_code', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class BonusSerializer(serializers.ModelSerializer):
    """Сериализатор для бонуса."""
    user = UserSerializer(read_only=True)
    source_user = UserSerializer(read_only=True)
    bonus_type_display = serializers.CharField(source='get_bonus_type_display', read_only=True)
    
    class Meta:
        model = Bonus
        fields = [
            'id', 'user', 'source_user', 'bonus_type', 'bonus_type_display',
            'amount', 'description', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RegisterSerializer(serializers.Serializer):
    """Сериализатор для регистрации."""
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    referral_code = serializers.CharField(max_length=20, required=False, allow_blank=True)
    tariff_code = serializers.CharField(max_length=50, required=False, allow_blank=True)
    
    def validate_username(self, value):
        """Проверка уникальности username."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким именем уже существует")
        return value
    
    def validate_email(self, value):
        """Проверка уникальности email."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value
    
    def validate_referral_code(self, value):
        """Проверка существования referral_code."""
        if value:
            if not User.objects.filter(referral_code=value).exists():
                raise serializers.ValidationError("Реферальный код не найден")
        return value


class CompleteRegistrationSerializer(serializers.Serializer):
    """Сериализатор для завершения регистрации."""
    user_id = serializers.IntegerField()
    
    def validate_user_id(self, value):
        """Проверка существования пользователя."""
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден")
        
        # Проверяем, что у пользователя есть pending платеж
        if not Payment.objects.filter(user=user, status=Payment.PaymentStatus.PENDING).exists():
            raise serializers.ValidationError("У пользователя нет ожидающих платежей")
        
        return value

