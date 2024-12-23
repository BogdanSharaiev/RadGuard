from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import RadiationData, User, Alert
from ..serializers import RadiationDataSerializer

LEVELS = {
    'Low': 0.1,
    'Moderate': 0.3,
    'High': 0.5,
    'Critical': 1.0,
}


class RadiationDataList(APIView):
    def get(self, request):
        radiation_data = RadiationData.objects.all()
        serializer = RadiationDataSerializer(radiation_data, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RadiationDataSerializer(data=request.data)
        if serializer.is_valid():
            radiation_data = serializer.save()

            if radiation_data.radiation_level >= LEVELS['Critical']:
                alert_level = 'Critical'
                alert_message = (f"Critical alert: Radiation level in sensor '{radiation_data.sensor.sensor_name}' "
                                 f"at {radiation_data.sensor.location.city} is "
                                 f"extremely high: {radiation_data.radiation_level} mSv/h.")
            elif radiation_data.radiation_level >= LEVELS['High']:
                alert_level = 'High'
                alert_message = (f"High alert: Radiation level in sensor "
                                 f"'{radiation_data.sensor.sensor_name}' at {radiation_data.sensor.location.city} "
                                 f"is high: {radiation_data.radiation_level} mSv/h.")
            elif radiation_data.radiation_level >= LEVELS['Moderate']:
                alert_level = 'Moderate'
                alert_message = (f"Moderate alert: Radiation level in sensor "
                                 f"'{radiation_data.sensor.sensor_name}' at "
                                 f"{radiation_data.sensor.location.city} "
                                 f"is moderate: {radiation_data.radiation_level} mSv/h.")
            elif radiation_data.radiation_level >= LEVELS['Low']:
                alert_level = 'Low'
                alert_message = (f"Low alert: Radiation level in sensor "
                                 f"'{radiation_data.sensor.sensor_name}' "
                                 f"at {radiation_data.sensor.location.city} "
                                 f"is slightly elevated: {radiation_data.radiation_level} mSv/h.")
            else:
                alert_level = 'Normal'
                alert_message = (f"Radiation level in sensor '{radiation_data.sensor.sensor_name}'"
                                 f" at {radiation_data.sensor.location.city} "
                                 f"is normal: {radiation_data.radiation_level} mSv/h.")

            Alert.objects.create(
                sensor=radiation_data.sensor,
                alert_message=alert_message,
                alert_level=alert_level,
            )

            if alert_level in ['High', 'Critical']:
                user = User.objects.get(sensor=radiation_data.sensor)
                email = user.email
                if email:
                    send_mail(
                        subject=f"{alert_level} Radiation Alert",
                        message=alert_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                    )

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
