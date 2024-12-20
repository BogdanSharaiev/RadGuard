from django.urls import path
from .views import GenerateReport

urlpatterns = [
    path('generate-report/<int:sensor_id>/<str:start_date>/<str:end_date>/', GenerateReport.as_view(), name='generate-report'),
]