# File Upload to S3 Application

A simple Python Flask web application that allows users to upload files directly to an Amazon S3 bucket.

## Features

- 📁 Simple web interface for file uploads
- 🔒 Secure file handling with filename sanitization
- ☁️ Direct upload to Amazon S3
- ✅ File type validation
- 🎨 Clean, responsive UI
- 📊 Health check endpoint
- 🔧 Environment-based configuration

## Setup Instructions

### 1. Configure AWS Credentials

Copy the environment template and fill in your AWS details:

```bash
cp .env.template .env
```

Edit the `.env` file with your actual values:
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `AWS_REGION`: Your preferred AWS region (e.g., us-east-1)
- `S3_BUCKET_NAME`: Name of your S3 bucket

### 2. Create S3 Bucket

Make sure you have an S3 bucket created with the appropriate permissions:

1. Log into AWS Console
2. Go to S3 service
3. Create a new bucket or use existing one
4. Ensure your AWS credentials have `s3:PutObject` permission for the bucket

### 3. Install Dependencies

The dependencies are already installed in the virtual environment, but if you need to reinstall:

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python file_upload_app.py
```

The application will start on `http://localhost:5000`

## Usage

1. Open your web browser and go to `http://localhost:5000`
2. Select a file using the file picker
3. Click "Upload File"
4. The file will be uploaded to your configured S3 bucket with a unique name

## Configuration

### Allowed File Types

The application currently allows these file types:
- Documents: txt, pdf, doc, docx, csv, xlsx
- Images: png, jpg, jpeg, gif

You can modify the `ALLOWED_EXTENSIONS` set in `file_upload_app.py` to add or remove file types.

### File Naming

Uploaded files are automatically renamed with:
- Timestamp (YYYYMMDD_HHMMSS)
- Unique ID (8 characters)
- Original filename (sanitized)

Example: `20241014_143022_a1b2c3d4_document.pdf`

## API Endpoints

- `GET /` - Upload form interface
- `POST /` - File upload endpoint
- `GET /health` - Health check and configuration status

## Security Notes

- Never commit your `.env` file to version control
- Use IAM roles with minimal required permissions
- Consider adding file size limits for production use
- The application includes basic CSRF protection via Flask's secret key

## Troubleshooting

### S3 Client Not Configured
- Check your `.env` file has correct AWS credentials
- Verify your AWS credentials have S3 access
- Ensure the S3 bucket exists and is accessible

### Upload Failures
- Check bucket permissions
- Verify AWS region matches your bucket's region
- Check file size limits (Flask default is 16MB)

## Production Considerations

For production deployment, consider:
- Using a production WSGI server (gunicorn, uWSGI)
- Adding file size limits
- Implementing user authentication
- Using AWS IAM roles instead of access keys
- Adding logging and monitoring
- Setting up HTTPS
- Adding rate limiting