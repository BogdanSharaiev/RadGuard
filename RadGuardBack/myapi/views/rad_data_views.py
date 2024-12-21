from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import RadiationData, Sensor, User, Alert
from ..serializers import RadiationDataSerializer
from django.core.mail import send_mail
from django.conf import settings


CRITICAL_RADIATION_LEVEL = 0.5


class RadiationDataList(APIView):
    def get(self, request):
        radiation_data = RadiationData.objects.all()
        serializer = RadiationDataSerializer(radiation_data, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RadiationDataSerializer(data=request.data)
        if serializer.is_valid():
            radiation_data = serializer.save()

            if radiation_data.radiation_level > CRITICAL_RADIATION_LEVEL:
                sensor = radiation_data.sensor
                user = User.objects.get(sensor=sensor.id)

                alert_message = (
                    f"Увага! У сенсорі '{sensor.sensor_name}' в місті '{sensor.location.city}' "
                    f"зафіксовано критичний рівень радіації: {radiation_data.radiation_level} мЗв/год."
                )
                Alert.objects.create(
                    sensor=sensor,
                    alert_message=alert_message,
                    alert_level="Critical",
                )

                email = user.email
                if email:
                    send_mail(
                        subject="Критичний рівень радіації",
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
