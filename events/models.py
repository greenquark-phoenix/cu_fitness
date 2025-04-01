from django.db import models
from django.contrib.auth.models import User

class FitnessEvent(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=[
        ('upcoming', 'Upcoming'),
        ('popular', 'Popular'),
        ('completed', 'Completed')
    ], default='upcoming')

    def __str__(self):
        return self.title

class EventParticipation(models.Model):
    event = models.ForeignKey(FitnessEvent, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')
