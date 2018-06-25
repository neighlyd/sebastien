from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Role(models.Model):
    role = models.CharField(max_length=15)

    def __str__(self):
        return self.role

    class Meta:
        ordering = ('role', )


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roles = models.ManyToManyField(Role, blank=True)
    wage = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)
            p = Profile.objects.get(user=instance)
            viewer = Role.objects.get(role='Viewer')
            p.roles.add(viewer)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def __str__(self):
        return '{0} {1}'.format(self.user.first_name, self.user.last_name)