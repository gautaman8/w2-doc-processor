# Document Processor

A Django REST API backend with Streamlit frontend for document processing.

## Project Structure

```
doc-processor/
├── shared_services/          # Shared utilities package
│   └── services/
│       └── s3_service.py     # S3 service with LocalStack support
├── doc_processor_backend/    # Django REST API
│   ├── w2_job_app/          # Main app with W2Job model
│   └── manage.py
├── frontend/                # Streamlit frontend
│   └── app.py
├── requirements.txt         # All dependencies
├── docker-compose.yml       # LocalStack setup
└── .env                     # Environment variables
```

## Setup & Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start LocalStack (for S3 simulation):**
   ```bash
   docker-compose up -d
   ```

3. **Setup Django database:**
   ```bash
   cd doc_processor_backend
   python manage.py migrate
   ```

4. **Run Django backend:**
   ```bash
   # Set Python path and run Django
   export PYTHONPATH="/Users/gautamansarangan/doc-processor:$PYTHONPATH"
   cd doc_processor_backend
   python manage.py runserver 8000
   ```

5. **Run Streamlit frontend (in new terminal):**
   ```bash
   cd frontend
   streamlit run app.py
   ```

## API Endpoints

- `POST /jobs/` - Create a new job with S3 signed URL
- `GET /jobs/{job_id}/` - Get job details
- `GET /jobs/bucket_info/` - Get S3 bucket information

## Usage

1. Open http://localhost:8501 in your browser
2. Click "Upload Document" to create a job
3. Upload your file using the provided signed URL
4. Check job status using the job ID

## S3 Integration

- **LocalStack S3** - Simulates AWS S3 locally
- **Auto-bucket creation** - Creates "w2-bucket" automatically
- **Folder structure** - `uploads/{job_id}/w2.pdf`
- **Real signed URLs** - Compatible with AWS S3

## Models

The `W2Job` model can be imported into other Django projects or Lambda functions:

```python
from w2_job_app.models import W2Job
```

## Shared Services

The `S3Service` can be used across multiple Django projects:

```python
from shared_services.services.s3_service import S3Service

s3_service = S3Service()
signed_url = s3_service.generate_presigned_url("uploads/file.pdf")
```
