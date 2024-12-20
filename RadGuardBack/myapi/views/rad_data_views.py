from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import RadiationData
from ..serializers import RadiationDataSerializer


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
