from rest_framework import serializers
from .models import User, ReadBook
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'detail': 'Неверный email или пароль'})

        if not user.check_password(password):
            raise serializers.ValidationError({'detail': 'Неверный email или пароль'})

        if not user.is_active:
            raise serializers.ValidationError({'detail': 'Пользователь неактивен'})

        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'email': user.email,
            'user_id': user.id,
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'full_name', 'gender', 'birth_date', 'category', 'email', 'phone')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    gender_display = serializers.SerializerMethodField(read_only=True)
    category_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'full_name', 'gender', 'gender_display',
            'birth_date', 'category', 'category_display',
            'email', 'phone', 'password', 'password2'
        )

    def get_gender_display(self, obj):
        return obj.get_gender_display()

    def get_category_display(self, obj):
        return obj.get_category_display()

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Пароли не совпадают.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create(
            full_name=validated_data['full_name'],
            gender=validated_data['gender'],
            birth_date=validated_data['birth_date'],
            category=validated_data['category'],
            email=validated_data['email'],
            phone=validated_data['phone'],
        )
        user.set_password(validated_data['password'])
        user.save()

        # Генерация токенов
        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        # Возврат вместе с токенами
        return {
            'user': user,
            'tokens': tokens
        } 


class ReatingsSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'reitforusers')

class SendEmailConfirmationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
class PasswordResetConfirmSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)

# serializers.py

class ReadBookSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='book.title')
    author = serializers.CharField(source='book.author')
    image = serializers.ImageField(source='book.image')
    date_read = serializers.DateTimeField(format="%d.%m.%Y %H:%M")

    class Meta:
        model = ReadBook
        fields = ['title', 'author', 'image', 'date_read']


class UserCabinetSerializer(serializers.ModelSerializer):
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    read_books = serializers.SerializerMethodField()
    read_books_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'phone', 'gender', 'gender_display', 'birth_date', 'category', 'category_display', 'reitforusers', 'is_email_verified', 'read_books', 'read_books_count',
        ]

    def get_read_books(self, obj):
        books = obj.read_books.select_related('book').order_by('-date_read')[:10] 
        return ReadBookSerializer(books, many=True).data

    def get_read_books_count(self, obj):
        return obj.read_books.count()
