import streamlit as st
import requests
import json

st.title("Document Processor")

# Main upload section
st.header("Upload Document")

# File uploader (always visible)
uploaded_file = st.file_uploader("Choose a file", type=['pdf'])

if uploaded_file is not None:
    st.write(f"**Selected file:** {uploaded_file.name}")
    st.write(f"**File size:** {uploaded_file.size} bytes")
    st.write(f"**File type:** {uploaded_file.type}")
    
    # Upload button (only show when file is selected)
    if st.button("Upload Document"):
        try:
            # Call API endpoint - POST /jobs/
            response = requests.post("http://localhost:8000/jobs/")
            
            if response.status_code == 201:
                data = response.json()
                job_id = data.get("job_id")
                signed_url = data.get("signed_url")
                
                st.success(f"Job ID: {job_id}")
                st.info("Uploading file to S3...")
                
                # Upload file to signed URL - send as binary data
                file_data = uploaded_file.getvalue()
                upload_response = requests.put(signed_url, data=file_data)
                
                # Display results
                st.write(f"**Upload Status Code:** {upload_response.status_code}")
                st.write(f"**Upload Response:** {upload_response.text}")
                
                if upload_response.status_code in [200, 204]:
                    st.success("✅ File uploaded successfully to S3!")
                    
                    # Test downloading the file (only show if there's an error)
                    download_response = requests.get(signed_url.split('?')[0])  # Remove query params for GET
                    
                    if download_response.status_code != 200:
                        st.write("🔍 Testing file download...")
                        st.error(f"❌ Failed to download file: {download_response.status_code}")
                        
                else:
                    st.error(f"❌ Upload failed with status {upload_response.status_code}")
                    st.write(f"**Error details:** {upload_response.text}")
            else:
                st.error(f"API Error: {response.status_code}")
                if response.text:
                    st.error(f"Error details: {response.text}")
                
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to local server. Make sure it's running on localhost:8000")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Sidebar for additional features
with st.sidebar:
    st.header("Additional Features")
    
    # Check Job Status
    st.subheader("Check Job Status")
    job_id_input = st.text_input("Enter Job ID:", key="job_id_input")
    if st.button("Check Status", key="check_status_btn") and job_id_input:
        try:
            status_response = requests.get(f"http://localhost:8000/jobs/{job_id_input}/")
            if status_response.status_code == 200:
                job_data = status_response.json()
                st.success("Job found!")
                st.json(job_data)
            else:
                st.error(f"Job not found or error: {status_response.status_code}")
        except Exception as e:
            st.error(f"Error checking status: {str(e)}")
    
    # Bucket Info
    st.subheader("S3 Bucket Info")
    if st.button("Get Bucket Info", key="bucket_info_btn"):
        try:
            bucket_response = requests.get("http://localhost:8000/jobs/bucket_info/")
            if bucket_response.status_code == 200:
                bucket_data = bucket_response.json()
                st.success("Bucket info retrieved!")
                st.json(bucket_data)
            else:
                st.error(f"Failed to get bucket info: {bucket_response.status_code}")
        except Exception as e:
            st.error(f"Error getting bucket info: {str(e)}")

# Instructions
st.markdown("---")
st.markdown("### Instructions:")
st.markdown("1. Select a PDF file using the file uploader")
st.markdown("2. Click 'Upload Document' to create job and upload")
st.markdown("3. File will be uploaded to S3 automatically")
st.markdown("4. Use sidebar features for additional operations")
