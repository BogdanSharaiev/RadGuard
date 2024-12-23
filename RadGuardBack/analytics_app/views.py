import os
import statistics
from collections import Counter
from datetime import datetime
from django.conf import settings
from myapi.models import Report, RadiationData, Sensor, Location
from myapi.serializers import ReportSerializer
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from utils import *


class GenerateReport(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, sensor_id: int, start_date: str, end_date: str) -> Response:
        user = request.user

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return Response({"error": "Invalid date format. Use 'YYYY-MM-DD'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sensor = Sensor.objects.get(id=sensor_id)
        except Sensor.DoesNotExist:
            return Response({"error": "Sensor not found"}, status=status.HTTP_404_NOT_FOUND)

        is_user_sensor = Sensor.objects.filter(id=sensor_id, user=user).first()
        if not is_user_sensor:
            return Response({"error": "Invalid sensor for user"}, status=status.HTTP_404_NOT_FOUND)

        radiation_data = RadiationData.objects.filter(
            sensor_id=sensor_id,
            measured_at__range=(start_date, end_date)
        ).order_by('measured_at')

        if not radiation_data.exists():
            return Response({"error": "No data available for the selected period"}, status=status.HTTP_404_NOT_FOUND)

        radiation_levels = [data.radiation_level for data in radiation_data]
        avg_radiation = sum(radiation_levels) / len(radiation_levels)
        min_radiation = min(radiation_levels)
        max_radiation = max(radiation_levels)
        median_radiation = statistics.median(radiation_levels)
        mode_radiation = Counter(radiation_levels).most_common(1)[0][0]
        std_deviation = statistics.stdev(radiation_levels) if len(radiation_levels) > 1 else 0

        duration = (end_date - start_date).total_seconds() / 3600
        measurements_per_hour = len(radiation_levels) / float(duration) if duration > 0 else 0

        location = Location.objects.get(id=sensor.location.id)
        reports_dir = os.path.join(settings.BASE_DIR, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        report_name = f"звіт_про_рівень_радіації_{sensor_id}_{start_date.strftime('%Y%m%d')}_до_{end_date.strftime('%Y%m%d')}.pdf"
        report_path = os.path.join(reports_dir, report_name)

        c = canvas.Canvas(report_path, pagesize=letter)
        c.setFont("Helvetica", 14)
        c.drawString(50, 750, f"Radiation Level Report")
        c.drawString(50, 730, f"Sensor: {radiation_data.first().sensor.sensor_name}")
        c.drawString(50, 710, f"Location: {location.city}")
        c.drawString(50, 690, f"Longitude: {location.longitude}, Latitude: {location.latitude}")
        c.drawString(50, 670, f"Period: {start_date.date()} - {end_date.date()}")
        c.drawString(50, 650, f"Average radiation level: {avg_radiation:.2f}")
        c.drawString(50, 630, f"Minimum radiation level: {min_radiation:.2f}")
        c.drawString(50, 610, f"Maximum radiation level: {max_radiation:.2f}")
        c.drawString(50, 590, f"Median radiation level: {median_radiation:.2f}")
        c.drawString(50, 570, f"Mode radiation level: {mode_radiation:.2f}")
        c.drawString(50, 550, f"Standard Deviation: {std_deviation:.2f}")
        c.drawString(50, 530, f"Measurements per hour: {measurements_per_hour:.2f}")
        c.drawString(50, 490, f"Measurements count: {len(radiation_levels)}")
        c.save()

        relative_report_path = os.path.relpath(report_path, settings.BASE_DIR)
        report = Report.objects.create(
            user=user,
            sensor=sensor,
            report_name=f"Звіт про рівень радіації з {start_date.date()} по {end_date.date()}",
            report_path=relative_report_path,
        )

        serializer = ReportSerializer(report, many=False)
        return Response(serializer.data)


class PredictRad(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, location_id, hours):
        try:
            location = Location.objects.get(id=location_id)
            sensor = Sensor.objects.get(location=location)

            data = RadiationData.objects.filter(sensor=sensor).order_by('measured_at')

            if data.count() < 2:
                return Response({"error": "Not enough data for prediction"}, status=400)

            times = []
            radiation_levels = []
            first_time = data.first().measured_at

            for obj in data:
                time_diff = (obj.measured_at - first_time).total_seconds()
                times.append(time_diff)
                radiation_levels.append(float(obj.radiation_level))

            predict_time = hours * 3600
            predict_time += (data.last().measured_at - first_time).total_seconds()
            predicted_radiation = predict_radiation(times, radiation_levels, predict_time)
            predicted_radiation = max(predicted_radiation, 0)

            return Response({"predicted_radiation": predicted_radiation}, status=200)

        except Location.DoesNotExist:
            return Response({"error": "Location not found"}, status=404)
        except Sensor.DoesNotExist:
            return Response({"error": "Sensor not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


def predict_radiation(times, radiation_levels, predict_time):
    if len(times) < 2 or len(radiation_levels) < 2:
        raise ValueError("Not enough data for prediction")

    n = len(times)
    mean_time = sum(times) / n
    mean_radiation = sum(radiation_levels) / n

    numerator = sum((times[i] - mean_time) * (radiation_levels[i] - mean_radiation) for i in range(n))
    denominator = sum((times[i] - mean_time) ** 2 for i in range(n))

    if denominator == 0:
        raise ValueError("Cannot fit a line, all times are the same")

    slope = numerator / denominator
    intercept = mean_radiation - slope * mean_time

    predicted_radiation = slope * predict_time + intercept
    return predicted_radiation
