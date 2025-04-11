from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from workouts.models import WorkoutPlan, SubPlan


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    allergies = models.CharField(max_length=255, blank=True)
    dietary_preferences = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, blank=True)
    current_weight = models.FloatField(null=True, blank=True)
    selected_workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.SET_NULL, null=True, blank=True)
    selected_sub_plan = models.ForeignKey(SubPlan, on_delete=models.SET_NULL, null=True, blank=True)
    selected_workout_plans = models.ManyToManyField(WorkoutPlan, blank=True, related_name='selected_by_users')
    selected_sub_plans = models.ManyToManyField(SubPlan, blank=True, related_name='selected_by_users')

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def user_post_save(sender, **kwargs):
    if kwargs['created'] and not kwargs['raw']:
        user = kwargs['instance']
        try:
            UserProfile.objects.get(user=user)

        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=user)
