import uuid
from django.db import models
from django.utils import timezone
from decimal import Decimal

class W2Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job_id = models.CharField(max_length=100, unique=True)
    filename = models.CharField(max_length=255)
    file_uploaded = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='started')
    signed_url = models.URLField(max_length=500, null=True, blank=True)
    external_upload = models.BooleanField(default=False)
    external_data_update = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'w2_jobs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.filename} - {self.job_id}"

class W2Data(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    w2_job = models.OneToOneField(
        W2Job, 
        on_delete=models.CASCADE, 
        related_name='w2_data',
        null=True, 
        blank=True
    )
    ein = models.CharField(max_length=20, null=True, blank=True)
    ssn = models.CharField(max_length=20, null=True, blank=True)
    wages_box1 = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    federal_tax_withheld_box2 = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'w2_data'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"W2Data for {self.w2_job.job_id if self.w2_job else 'No Job'}"
