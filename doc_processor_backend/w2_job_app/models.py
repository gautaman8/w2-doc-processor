import uuid
from django.db import models
from django.utils import timezone

class W2Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job_id = models.CharField(max_length=100, unique=True)
    filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField(null=True, blank=True)
    file_type = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, default='started')
    signed_url = models.URLField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'w2_jobs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.filename} - {self.job_id}"
