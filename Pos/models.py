from django.db import models
from Location.models import Location,User


class Pos(models.Model):
    pos_name = models.CharField(max_length=200)
    pos_code = models.CharField(max_length=50, unique=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='pos_devices')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pos_devices')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pos_code:
            # Count existing POS for this location to generate a sequence
            count = Pos.objects.filter(location=self.location).count() + 1
            self.pos_code = f"LOC{self.location.id:03d}-{count:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.pos_name} ({self.pos_code}) - {self.location.location_name}"

    class Meta:
        ordering = ['-created_at']

