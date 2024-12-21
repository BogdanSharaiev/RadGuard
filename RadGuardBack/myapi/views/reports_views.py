from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Report
from ..serializers import ReportSerializer


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
