import uuid
import time
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import W2Job
from .serializers import W2JobSerializer, CreateJobResponseSerializer
from shared_services.services.s3_service import S3Service

class W2JobViewSet(viewsets.ModelViewSet):
    queryset = W2Job.objects.all()
    serializer_class = W2JobSerializer
    permission_classes = [AllowAny]
    lookup_field = 'job_id'

    def create(self, request):
        """Create a new job - POST /jobs/"""
        # Generate job ID with timestamp and UUID
        timestamp = str(int(time.time()))
        unique_id = str(uuid.uuid4())[:8]
        job_id = f"{timestamp}_{unique_id}"
        
        # Generate S3 object key with folder structure
        object_key = f"uploads/{job_id}/w2.pdf"
        
        # Use S3Service to generate signed URL
        s3_service = S3Service()
        signed_url = s3_service.generate_presigned_url(object_key)
        
        if not signed_url:
            return Response(
                {"error": "Failed to generate signed URL"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Create W2Job record
        job_obj = W2Job.objects.create(
            job_id=job_id,
            filename="w2.pdf",
            status="started",
            signed_url=signed_url
        )
        
        # Return only the required fields
        response_data = {
            "job_id": job_id,
            "status": "started",
            "signed_url": signed_url
        }
        
        serializer = CreateJobResponseSerializer(response_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, job_id=None):
        """Get job details - GET /jobs/{job_id}/"""
        try:
            job_obj = W2Job.objects.get(job_id=job_id)
            serializer = self.get_serializer(job_obj)
            return Response(serializer.data)
        except W2Job.DoesNotExist:
            return Response(
                {"error": "Job not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def bucket_info(self, request):
        """Get S3 bucket information - GET /jobs/bucket_info/"""
        s3_service = S3Service()
        bucket_info = s3_service.get_bucket_info()
        return Response(bucket_info)

    def partial_update(self, request, job_id=None):
        """Update job - PATCH /jobs/{job_id}/"""
        try:
            job = W2Job.objects.get(job_id=job_id)
            
            # Update only the fields that are passed in the request
            for field, value in request.data.items():
                if hasattr(job, field):
                    setattr(job, field, value)
            
            job.save()
            
            # Return updated job data
            serializer = self.get_serializer(job)
            return Response(serializer.data)
        except W2Job.DoesNotExist:
            return Response(
                {"error": "Job not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to update job: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
