from .models import User
from .serializers import RegisterSerializer, ReatingsSerializers, PasswordResetConfirmSerializer,SendEmailConfirmationSerializer, CustomTokenObtainPairSerializer,UserCabinetSerializer
from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView
#from .serializers import EmailTokenObtainPairSerializer  
from rest_framework.generics import GenericAPIView
from .utils import generate_reset_code, generate_email_code
from django.core.mail import send_mail
from django.conf import settings

class CustomTokenObtainPairView(APIView):
    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

class CategoryListView(APIView):
    def get(self, request):
        categories = [
            {"id": choice[0], "name": choice[1]}
            for choice in User.Category.choices
        ]
        return Response(categories)

class UserRegister(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def list(self, request, *args, **kwargs):
        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            
            response_data = {
                'user': RegisterSerializer(result['user']).data,
                'tokens': result['tokens']
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class IncreaseUserRatingView(mixins.ListModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = ReatingsSerializers
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = request.user
        try:
            user.reitforusers = int(user.reitforusers) + 1
        except:
            user.reitforusers = 1
        user.save()

        serializer = self.get_serializer(user)
        return Response({
            'message': 'Ваш рейтинг обновлён',
            'new_rating': user.reitforusers,
            'user': serializer.data
        })

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh токен обязателен."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Вы успешно вышли из аккаунта."}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({"detail": "Недействительный токен."}, status=status.HTTP_400_BAD_REQUEST)

class SendEmailConfirmationView(GenericAPIView):
    serializer_class = SendEmailConfirmationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'detail': 'Пользователь с таким email не найден.'}, status=status.HTTP_404_NOT_FOUND)

            code = generate_email_code(user)

            send_mail(
                subject='Код подтверждения почты',
                message=f'Ваш код подтверждения: {code}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )

            return Response({'detail': 'Код отправлен на почту.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SendPasswordResetCodeView(GenericAPIView):
    serializer_class = SendEmailConfirmationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'detail': 'Пользователь с таким email не найден.'}, status=status.HTTP_404_NOT_FOUND)

            code = generate_reset_code()
            user.reset_password_code = code
            user.save()

            send_mail(
                subject='Сброс пароля',
                message=f'Ваш код для сброса пароля: {code}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )

            return Response({'detail': 'Код сброса пароля отправлен на почту.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PasswordResetConfirmView(GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            new_password = serializer.validated_data['new_password']

            try:
                user = User.objects.get(reset_password_code=code)
            except User.DoesNotExist:
                return Response({'detail': 'Неверный код подтверждения.'}, status=400)

            user.set_password(new_password)
            user.reset_password_code = generate_reset_code()
            user.save()

            return Response({'detail': 'Пароль успешно изменён.'})

        return Response(serializer.errors, status=400)


class UserCabinetView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserCabinetSerializer(request.user)
        return Response(serializer.data)


