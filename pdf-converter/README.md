# PDF Converter Container

Converts text files from S3 to PDF format.

## Build

```bash
docker build -t pdf-converter .
```

## Run

```bash
docker run --rm \
  -e AWS_ACCESS_KEY_ID=your_access_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret_key \
  -e AWS_DEFAULT_REGION=us-east-1 \
  -e SOURCE_BUCKET=batch-poc-input-bucket-123456789 \
  -e OBJECT_KEY=test_file.txt \
  -e DEST_BUCKET=batch-poc-output-bucket-123456789 \
  pdf-converter
```

## Environment Variables

- `SOURCE_BUCKET`: Source S3 bucket name
- `OBJECT_KEY`: Source object key/filename
- `DEST_BUCKET`: Destination S3 bucket name
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_DEFAULT_REGION`: AWS region

## API Version
If running the API version, then flask>=2.0.0 must be installed as a requirement, and the build script should be modified to build and push the image with the :api tag instead of the:latest tag for testing. The API step function workflow is configured to look for the :api tag for the image pull.
