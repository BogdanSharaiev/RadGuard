import os
from datetime import datetime
from django.conf import settings
from myapi.models import Report, RadiationData, Sensor, Location
from myapi.serializers import ReportSerializer
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from utils import *


class GenerateReport(APIView):
    def get(self, request, sensor_id: int, start_date: str, end_date: str) -> Response:
        print(request)
        token = get_token_from_request(request)
        user = get_user_from_token(token)

        if not token or not user:
            return Response({"error": "Invalid token or user not found"}, status=status.HTTP_401_UNAUTHORIZED)

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
            return Response({"error": "Дані для заданого періоду відсутні"}, status=status.HTTP_404_NOT_FOUND)

        radiation_levels = [data.radiation_level for data in radiation_data]
        avg_radiation = sum(radiation_levels) / len(radiation_levels)
        min_radiation = min(radiation_levels)
        max_radiation = max(radiation_levels)

        location = Location.objects.get(id=sensor.location.id)
        print(location)

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
        c.drawString(50, 590, f"Measurements count: {len(radiation_levels)}")
        c.save()

        relative_report_path = os.path.relpath(report_path, settings.BASE_DIR)
        report = Report.objects.create(
            user=user,
            sensor=Sensor.objects.get(id=sensor_id),
            report_name=f"Звіт про рівень радіації з {start_date.date()} по {end_date.date()}",
            report_path=relative_report_path,
        )

        serializer = ReportSerializer(report, many=False)
        return Response(serializer.data)


class PredictRad(APIView):
    def get(self, request, location_id, hours):
        try:
            location = Location.objects.get(id=location_id)

            sensor = Sensor.objects.get(location=location)

            data = RadiationData.objects.filter(sensor=sensor)

            times = []
            radiation_levels = []

            last_time = None
            for obj in data:
                if last_time is None:
                    last_time = obj.measured_at

                time_diff = (obj.measured_at - last_time).total_seconds() / 3600
                times.append(time_diff)
                radiation_levels.append(float(obj.radiation_level))

            n = len(times)

            sum_x = sum(times)
            sum_y = sum(radiation_levels)
            sum_x2 = sum(x ** 2 for x in times)
            sum_xy = sum(times[i] * radiation_levels[i] for i in range(n))

            beta_1 = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
            beta_0 = (sum_y - beta_1 * sum_x) / n

            future_time = times[-1] + hours
            future_radiation = beta_0 + beta_1 * future_time

            future_radiation = max(future_radiation, 0)

            response_data = {
                "sensor": {
                    "id": sensor.id,
                    "name": sensor.sensor_name,
                    "status": sensor.status
                },
                "location": {
                    "id": location.id,
                    "city": location.city,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "description": location.description or "No description"
                },
                "forecast": {
                    "hours": hours,
                    "predicted_radiation_level": round(future_radiation, 2),
                    "unit": "μSv/h"
                }
            }

            return Response(response_data)

        except Location.DoesNotExist:
            return Response(
                {"error": "Location with the specified ID does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Sensor.DoesNotExist:
            return Response(
                {"error": "Sensor for the specified location does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred during radiation prediction: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
