import uuid
import time
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import W2Job
from .serializers import W2JobSerializer, CreateJobResponseSerializer

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
        
        # Mock signed URL
        signed_url = f"https://mock-bucket.s3.amazonaws.com/uploads/{job_id}?signature=mock_signature"
        
        # Create W2Job record
        job_obj = W2Job.objects.create(
            job_id=job_id,
            filename="",
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
