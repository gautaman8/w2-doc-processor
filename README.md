# Document Processor

A Django REST API backend with Streamlit frontend for document processing.

## Project Structure

```
doc-processor/
├── doc_processor_backend/     # Django REST API
│   ├── w2_job_app/           # Main app with W2Job model
│   └── manage.py
├── frontend/                 # Streamlit frontend
│   └── app.py
└── requirements.txt          # All dependencies
```

## Setup & Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Django database:**
   ```bash
   cd doc_processor_backend
   python manage.py migrate
   ```

3. **Run Django backend:**
   ```bash
   cd doc_processor_backend
   python manage.py runserver 8000
   ```

4. **Run Streamlit frontend (in new terminal):**
   ```bash
   cd frontend
   streamlit run app.py
   ```

## API Endpoints

- `POST /jobs/` - Create a new job
- `GET /jobs/{job_id}/` - Get job details

## Usage

1. Open http://localhost:8501 in your browser
2. Click "Upload Document" to create a job
3. Upload your file using the provided signed URL
4. Check job status using the job ID

## Models

The `W2Job` model can be imported into other Django projects or Lambda functions:

```python
from w2_job_app.models import W2Job
```
