from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'
        managed = True

    def __str__(self):
        return self.username


class Location(models.Model):
    id = models.AutoField(primary_key=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    city = models.CharField(max_length=50)
    description = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'locations'
        managed = True

    def __str__(self):
        return self.city


class Sensor(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sensor_name = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    last_update = models.DateTimeField(auto_now=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'sensors'
        managed = True

    def __str__(self):
        return self.sensor_name


class RadiationData(models.Model):
    id = models.AutoField(primary_key=True)
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    radiation_level = models.DecimalField(max_digits=5, decimal_places=2)
    measured_at = models.DateTimeField(auto_now_add=True)
    alert_triggered = models.BooleanField(default=False)

    class Meta:
        db_table = 'radiation_data'
        managed = True

    def __str__(self):
        return f"{self.sensor.sensor_name} - {self.radiation_level}"


class Alert(models.Model):
    id = models.AutoField(primary_key=True)
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    alert_message = models.CharField(max_length=255)
    alert_level = models.CharField(max_length=20)
    triggered_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        db_table = 'alerts'
        managed = True

    def __str__(self):
        return f"Alert {self.alert_level} - {self.alert_message}"


class Report(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sensor = models.ForeignKey(Sensor, on_delete=models.SET_NULL, null=True, blank=True)
    report_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    report_path = models.CharField(max_length=255)

    class Meta:
        db_table = 'reports'
        managed = True

    def __str__(self):
        return self.report_name

