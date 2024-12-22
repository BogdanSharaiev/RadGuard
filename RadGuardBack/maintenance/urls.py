from django.urls import path

from .views import PostgresDBManagementView

urlpatterns = [
    path('db-management/<str:action>/', PostgresDBManagementView.as_view(), name='db-management'),
]
