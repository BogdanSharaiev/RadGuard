from django.contrib.auth.hashers import check_password
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import Sensor, Report
from ..models import User
from ..permissions import IsAdminUserPermission
from ..serializers import UserSerializer, SensorSerializer, ReportSerializer


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"detail": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed("Invalid credentials")

        if not check_password(password, user.password):
            raise AuthenticationFailed("Invalid credentials")

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            'access': access_token,
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)


class UserList(APIView):
    permission_classes = []

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUserPermission()]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        serializer = UserSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSensorsList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        sensors = Sensor.objects.filter(user=user)
        serializer = SensorSerializer(sensors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        if request.user.role == 'admin' or request.user.id == id:
            try:
                user = User.objects.get(id=id)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        raise PermissionDenied("You do not have permission to view this user.")

    def put(self, request, id):
        if request.user.role == 'admin' or request.user.id == id:
            try:
                user = User.objects.get(id=id)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            if request.user.role != 'admin':
                data = request.data.copy()
                data.pop('role', None)
                serializer = UserSerializer(user, data=data)
            else:
                serializer = UserSerializer(user, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        raise PermissionDenied("You do not have permission to modify this user.")

    def delete(self, request, id):
        if request.user.role == 'admin':
            try:
                user = User.objects.get(id=id)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            user.delete()
            return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

        raise PermissionDenied("You do not have permission to delete this user.")


class UserReport(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        report_data = Report.objects.filter(user=id)
        if not report_data.exists():
            return Response({'message': 'No reports found for this user'}, status=status.HTTP_200_OK)

        serializer = ReportSerializer(report_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
