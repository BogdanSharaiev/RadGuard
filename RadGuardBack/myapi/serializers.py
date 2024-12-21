from rest_framework import serializers
from .models import User, Location, Sensor, RadiationData, Alert, Report
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(
        choices=[('user', 'User'), ('admin', 'Admin')],
        default='user'
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'created_at', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if password:
            validated_data['password'] = make_password(password)
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.get('password', None)
        if password:
            validated_data['password'] = make_password(password)

        return super().update(instance, validated_data)



class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'latitude', 'longitude', 'city', 'description']


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ['id', 'sensor_name', 'status', 'last_update', 'location','user']


class RadiationDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = RadiationData
        fields = ['id', 'sensor', 'radiation_level', 'measured_at', 'alert_triggered']


class AlertSerializer(serializers.ModelSerializer):

    class Meta:
        model = Alert
        fields = ['id', 'sensor', 'alert_message', 'alert_level', 'triggered_at', 'resolved']


class ReportSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    sensor = serializers.PrimaryKeyRelatedField(queryset=Sensor.objects.all(), required=True)
    report_path = serializers.CharField(required=True)

    class Meta:
        model = Report
        fields = ['id', 'user', 'sensor', 'report_name', 'created_at', 'report_path']
