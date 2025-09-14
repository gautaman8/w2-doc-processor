import streamlit as st
import requests
import json

st.title("Document Processor")

# Upload button
if st.button("Upload Document"):
    try:
        # Call API endpoint - POST /jobs/
        response = requests.post("http://localhost:8000/jobs/")
        
        if response.status_code == 201:
            data = response.json()
            job_id = data.get("job_id")
            signed_url = data.get("signed_url")
            
            st.success(f"Job ID: {job_id}")
            st.info("Please upload your file using the signed URL")
            
            # File uploader
            uploaded_file = st.file_uploader("Choose a file", type=['pdf'])
            
            if uploaded_file is not None:
                # Upload file to signed URL - send as binary data like curl
                file_data = uploaded_file.getvalue()
                upload_response = requests.put(signed_url, data=file_data)
                
                print(f"Signed URL: {signed_url}")
                print(f"File data: {file_data}")
                print("Request.data: ", upload_response.request.body)
                if upload_response.status_code in [200, 201, 204]:
                    st.success("File uploaded successfully!")
                    
                    # Show job status
                    # status_response = requests.get(f"http://localhost:8000/jobs/{job_id}/")
                    # if status_response.status_code in [200, 201, 204]:
                    #     job_data = status_response.json()
                    #     st.info(f"Job Status: {job_data.get('status')}")
                else:
                    st.error(f"Failed to upload file: {upload_response.text}")
        else:
            st.error(f"API Error: {response.status_code}")
            if response.text:
                st.error(f"Error details: {response.text}")
            
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to local server. Make sure it's running on localhost:8000")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Add a section to check job status manually
st.divider()
st.subheader("Check Job Status")

job_id_input = st.text_input("Enter Job ID to check status:")
if st.button("Check Status") and job_id_input:
    try:
        status_response = requests.get(f"http://localhost:8000/jobs/{job_id_input}/")
        if status_response.status_code == 200:
            job_data = status_response.json()
            st.success(f"Job found!")
            st.json(job_data)
        else:
            st.error(f"Job not found or error: {status_response.status_code}")
    except Exception as e:
        st.error(f"Error checking status: {str(e)}")
