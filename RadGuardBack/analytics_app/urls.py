from django.urls import path
from .views import GenerateReport, PredictRad

urlpatterns = [
    path('generate-report/<int:sensor_id>/<str:start_date>/<str:end_date>/', GenerateReport.as_view(), name='generate-report'),
    path('predict-rad/<int:location_id>/<int:hours>/', PredictRad.as_view(), name='predict-rad')
]