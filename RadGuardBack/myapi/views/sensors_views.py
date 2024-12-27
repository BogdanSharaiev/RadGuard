from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Sensor, RadiationData
from ..serializers import SensorSerializer, RadiationDataSerializer


class SensorList(APIView):
    def get(self, request):
        if request.user.role == 'admin':
            sensors = Sensor.objects.all()
            serializer = SensorSerializer(sensors, many=True)
            return Response(serializer.data)
        raise PermissionDenied("You do not have permission to view this sensors.")

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
        if request.user.role == 'admin':
            try:
                sensor = Sensor.objects.get(id=id)
            except Sensor.DoesNotExist:
                return Response({'error': 'Sensor not found'}, status=status.HTTP_404_NOT_FOUND)

            sensor.delete()
            return Response({'message': 'Sensor deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        raise PermissionDenied("You do not have permission to change this sensor.")
