from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Alert
from ..serializers import AlertSerializer


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
