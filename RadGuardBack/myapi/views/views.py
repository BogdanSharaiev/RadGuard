from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from RadGuardBack.myapi.models import User, Location, Sensor, RadiationData, Alert, Report
from RadGuardBack.myapi.serializers import (
    UserSerializer, LocationSerializer,
    SensorSerializer, RadiationDataSerializer,
    AlertSerializer, ReportSerializer
)


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

        if not check_password(password, user.password_hash):
            raise AuthenticationFailed("Invalid credentials")

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            'access': access_token,
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)



class UserList(APIView):
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
    def get(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        sensors = Sensor.objects.filter(user=user)
        serializer = SensorSerializer(sensors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDetail(APIView):
    def get(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# 2. Location (Локації)
class LocationList(APIView):
    def get(self, request):
        locations = Location.objects.all()
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LocationDetail(APIView):
    def get(self, request, id):
        try:
            location = Location.objects.get(id=id)
        except Location.DoesNotExist:
            return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = LocationSerializer(location)
        return Response(serializer.data)

    def put(self, request, id):
        try:
            location = Location.objects.get(id=id)
        except Location.DoesNotExist:
            return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = LocationSerializer(location, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            location = Location.objects.get(id=id)
        except Location.DoesNotExist:
            return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)

        location.delete()
        return Response({'message': 'Location deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# 3. Sensor (Датчики)
class SensorList(APIView):
    def get(self, request):
        sensors = Sensor.objects.all()
        serializer = SensorSerializer(sensors, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SensorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SensorDataList(APIView):
    def get(self, request, id):
        try:
            sensor = Sensor.objects.get(id=id)
        except Sensor.DoesNotExist:
            return Response({'error': 'Sensor not found'}, status=status.HTTP_404_NOT_FOUND)

        data = RadiationData.objects.filter(sensor=sensor)
        serializer = RadiationDataSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SensorDetail(APIView):
    def get(self, request, id):
        try:
            sensor = Sensor.objects.get(id=id)
        except Sensor.DoesNotExist:
            return Response({'error': 'Sensor not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SensorSerializer(sensor)
        return Response(serializer.data)

    def put(self, request, id):
        try:
            sensor = Sensor.objects.get(id=id)
        except Sensor.DoesNotExist:
            return Response({'error': 'Sensor not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SensorSerializer(sensor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            sensor = Sensor.objects.get(id=id)
        except Sensor.DoesNotExist:
            return Response({'error': 'Sensor not found'}, status=status.HTTP_404_NOT_FOUND)

        sensor.delete()
        return Response({'message': 'Sensor deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# 4. RadiationData (Радіаційні дані)
class RadiationDataList(APIView):
    def get(self, request):
        radiation_data = RadiationData.objects.all()
        serializer = RadiationDataSerializer(radiation_data, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RadiationDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RadiationDataDetail(APIView):
    def get(self, request, id):
        try:
            data = RadiationData.objects.get(id=id)
        except RadiationData.DoesNotExist:
            return Response({'error': 'Radiation data not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = RadiationDataSerializer(data)
        return Response(serializer.data)

    def delete(self, request, id):
        try:
            data = RadiationData.objects.get(id=id)
        except RadiationData.DoesNotExist:
            return Response({'error': 'Radiation data not found'}, status=status.HTTP_404_NOT_FOUND)

        data.delete()
        return Response({'message': 'Radiation data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# 5. Alert (Попередження)
class AlertList(APIView):
    def get(self, request):
        alerts = Alert.objects.all()
        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AlertSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AlertDetail(APIView):
    def get(self, request, id):
        try:
            alert = Alert.objects.get(id=id)
        except Alert.DoesNotExist:
            return Response({'error': 'Alert not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AlertSerializer(alert)
        return Response(serializer.data)

    def delete(self, request, id):
        try:
            alert = Alert.objects.get(id=id)
        except Alert.DoesNotExist:
            return Response({'error': 'Alert not found'}, status=status.HTTP_404_NOT_FOUND)

        alert.delete()
        return Response({'message': 'Alert deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# 6. Report (Звіти)
class ReportList(APIView):
    def get(self, request):
        reports = Report.objects.all()
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportDetail(APIView):
    def get(self, request, id):
        try:
            report = Report.objects.get(id=id)
        except Report.DoesNotExist:
            return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ReportSerializer(report)
        return Response(serializer.data)

    def delete(self, request, id):
        try:
            report = Report.objects.get(id=id)
        except Report.DoesNotExist:
            return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)

        report.delete()
        return Response({'message': 'Report deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
