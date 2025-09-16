from rest_framework import serializers
from .models import W2Job

class W2JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = W2Job
        fields = ['id', 'job_id', 'filename', 'file_uploaded', 'status', 'signed_url', 'created_at', 'updated_at']
        read_only_fields = ['id', 'job_id', 'created_at', 'updated_at']

class CreateJobResponseSerializer(serializers.Serializer):
    job_id = serializers.CharField()
    status = serializers.CharField()
    signed_url = serializers.URLField()
