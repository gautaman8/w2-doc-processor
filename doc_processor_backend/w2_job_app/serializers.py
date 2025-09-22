from rest_framework import serializers
from .models import W2Job, W2Data

class W2DataSerializer(serializers.ModelSerializer):
    class Meta:
        model = W2Data
        fields = ['id', 'ein', 'ssn', 'wages_box1', 'federal_tax_withheld_box2', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class W2JobSerializer(serializers.ModelSerializer):
    w2_data = W2DataSerializer(required=False)
    
    class Meta:
        model = W2Job
        fields = [
            'id', 'job_id', 'filename', 'file_uploaded', 'status', 'signed_url', 
            'external_upload', 'external_data_update', 'w2_data_status', 'w2_data_status_msg',
            'w2_data', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'job_id', 'created_at', 'updated_at']
    
    def update(self, instance, validated_data):
        w2_data = validated_data.pop('w2_data', None)
        
        # Update W2Job fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Handle W2Data
        if w2_data:
            w2_data_obj, created = W2Data.objects.get_or_create(
                w2_job=instance,
                defaults=w2_data
            )
            if not created:
                for attr, value in w2_data.items():
                    setattr(w2_data_obj, attr, value)
                w2_data_obj.save()
        
        return instance

class CreateJobResponseSerializer(serializers.Serializer):
    job_id = serializers.CharField()
    status = serializers.CharField()
    signed_url = serializers.URLField()
