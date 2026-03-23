from django.db import models

class UserRegistrationModel(models.Model):
    name = models.CharField(max_length=100)
    loginid = models.CharField(unique=True, max_length=100)
    password = models.CharField(max_length=100)
    mobile = models.CharField(unique=True, max_length=10)  # Adjusted max_length to 10 for mobile numbers
    email = models.EmailField(unique=True, max_length=100)  # Use EmailField for better validation
    locality = models.CharField(max_length=100)
    address = models.TextField(max_length=1000)  # Use TextField for longer addresses
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    status = models.CharField(max_length=100, default='waiting')

    def __str__(self):
        return self.loginid

    class Meta:
        db_table = 'user_registrations'


class UserBehaviorTracking(models.Model):
    user = models.ForeignKey(UserRegistrationModel, on_delete=models.CASCADE, related_name='behavior_logs')
    date = models.DateField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    whatsapp = models.FloatField(default=0)
    instagram = models.FloatField(default=0)
    snapchat = models.FloatField(default=0)
    telegram = models.FloatField(default=0)
    facebook = models.FloatField(default=0)
    bereal = models.FloatField(default=0)
    tiktok = models.FloatField(default=0)
    wechat = models.FloatField(default=0)
    twitter = models.FloatField(default=0)
    linkedin = models.FloatField(default=0)
    messages = models.FloatField(default=0)
    total_screen_time = models.FloatField(default=0)
    hourly_opens = models.IntegerField(default=0)
    prediction_result = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.loginid} - {self.date}"

    class Meta:
        db_table = 'user_behavior_tracking'
        ordering = ['-timestamp']


class UserAlertSettings(models.Model):
    user = models.OneToOneField(UserRegistrationModel, on_delete=models.CASCADE, related_name='alert_settings')
    screen_time_limit = models.FloatField(default=5.0)  # hours
    unlock_limit = models.IntegerField(default=80)
    social_media_limit = models.FloatField(default=3.0)  # hours
    alerts_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"Alert Settings - {self.user.loginid}"

    class Meta:
        db_table = 'user_alert_settings'


