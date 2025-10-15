# Batch PoC - File Upload and Processing System

This system provides a complete file upload and processing pipeline using AWS S3, SQS, and a Python web application.

## Architecture Overview

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────────┐
│   Web Browser   │───▶│ Flask Upload │───▶│ S3 Bucket   │───▶│ SQS Queue        │
│                 │    │ Application  │    │ (Input)     │    │ (File Events)    │
└─────────────────┘    └──────────────┘    └─────────────┘    └──────────────────┘
                                                 │                        │
                                                 ▼                        ▼
                                           ┌─────────────┐    ┌──────────────────┐
                                           │ S3 Bucket   │    │ Processing       │
                                           │ (Output)    │◀───│ Application      │
                                           └─────────────┘    │ (SQS Consumer)   │
                                                              └──────────────────┘
```

## Components

### 1. CloudFormation Infrastructure (`BatchPoc.yml`)

**Resources Created:**
- **S3 Input Bucket**: Receives uploaded files
- **S3 Output Bucket**: Stores processed files
- **SQS Queue**: Receives notifications when files are uploaded
- **Dead Letter Queue**: Handles failed message processing
- **IAM Roles**: Permissions for S3 → SQS communication and user access
- **ECR Repositories**: Container registries for batch processing

**Key Features:**
- S3 bucket notifications automatically trigger SQS messages on file upload
- Encrypted storage and message queues
- Proper IAM permissions for secure access
- Dead letter queue for error handling

### 2. File Processing Consumer (`sqs_file_processor.py`)

An SQS consumer application that:
- Polls the SQS queue for file upload notifications
- Parses S3 event messages
- Processes files based on business logic
- Handles errors and retries
- Supports long polling for efficiency

## Setup Instructions

### Step 1: Deploy CloudFormation Infrastructure

1. **Deploy the stack:**
   ```bash
   aws cloudformation create-stack \
     --stack-name batch-poc-infrastructure \
     --template-body file://BatchPoc.yml \
     --capabilities CAPABILITY_IAM
   ```

2. **Wait for deployment to complete:**
   ```bash
   aws cloudformation wait stack-create-complete \
     --stack-name batch-poc-infrastructure
   ```

3. **Get the stack outputs:**
   ```bash
   aws cloudformation describe-stacks \
     --stack-name batch-poc-infrastructure \
     --query 'Stacks[0].Outputs'
   ```

## Usage Workflow

### 1. Upload Files
1. File is uploaded to S3 input bucket

### 2. Automatic Processing Trigger
1. S3 automatically sends a notification to SQS when file is uploaded
2. Message contains bucket name, object key, and event details
3. Message is queued for processing

### 3. File Processing
1. SQS consumer polls for messages
2. Processes each file notification
3. Can download file from S3, analyze, transform, etc.
4. Results can be stored in output bucket
5. Message is deleted from queue when processing succeeds

## SQS Message Format

When a file is uploaded to S3, the SQS queue receives a message like:

```json
{
  "Records": [
    {
      "eventVersion": "2.1",
      "eventSource": "aws:s3",
      "eventName": "ObjectCreated:Put",
      "eventTime": "2024-10-14T14:30:22.000Z",
      "awsRegion": "us-east-1",
      "s3": {
        "bucket": {
          "name": "batch-poc-input-bucket-123456789012"
        },
        "object": {
          "key": "20241014_143022_a1b2c3d4_document.pdf",
          "size": 1234567,
          "eTag": "d41d8cd98f00b204e9800998ecf8427e"
        }
      }
    }
  ]
}
```

## Customization

### File Processing Logic

Edit the `process_file()` method in `sqs_file_processor.py` to add your custom logic:

```python
def process_file(self, file_info: Dict) -> bool:
    bucket_name = file_info['bucket_name']
    object_key = file_info['object_key']
    
    # Your custom processing logic here:
    # - Download file from S3
    # - Analyze content
    # - Transform data
    # - Upload results to output bucket
    # - Update database
    # - Send notifications
    
    return True  # Return False if processing failed
```

### File Type Validation

Update `ALLOWED_EXTENSIONS` in `file_upload_app.py`:

```python
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'csv', 'xlsx'}
```

### Queue Configuration

Modify queue settings in the CloudFormation template:
- `VisibilityTimeoutSeconds`: How long messages are hidden during processing
- `MessageRetentionPeriod`: How long messages are kept in the queue
- `ReceiveMessageWaitTimeSeconds`: Long polling duration

## Monitoring and Troubleshooting

### CloudWatch Metrics
Monitor these metrics in AWS CloudWatch:
- S3 bucket object count and size
- SQS queue depth and message age
- Lambda/processing function errors (if using Lambda)

### Common Issues

1. **Files uploaded but no SQS messages:**
   - Check S3 bucket notification configuration
   - Verify SQS queue policy allows S3 to send messages

2. **SQS messages not being processed:**
   - Check AWS credentials in `.env` file
   - Verify queue URL is correct
   - Check processing application logs

3. **Permission errors:**
   - Ensure IAM policies are correctly configured
   - Check that S3 bucket and SQS queue are in the same region

### Logs
- Flask application: Console output
- SQS processor: Console output with detailed processing information
- AWS services: CloudWatch Logs

## Security Considerations

- All S3 buckets enforce encryption and deny unencrypted uploads
- SQS queues use AWS managed encryption
- IAM policies follow least privilege principle
- No public access to S3 buckets
- Secure transport (HTTPS/TLS) enforced

## Production Considerations

For production deployment:
1. Use AWS IAM roles instead of access keys
2. Deploy Flask app using a production WSGI server (gunicorn)
3. Add comprehensive logging and monitoring
4. Implement circuit breakers and retry logic
5. Use AWS Lambda for serverless processing
6. Add dead letter queue monitoring and alerting
7. Implement proper error handling and notification systems

# Workflow Diagrams

# BatchPoC End-to-End Workflow Diagram

```mermaid
graph TD
    %% File Upload
    A[User Uploads File] --> B[S3 Input Bucket]
    B --> C[S3 Event Notification]
    C --> D[SQS Queue]
    
    %% SQS Processing
    D --> E[Lambda SQS Processor]
    E --> F[Get Object Metadata]
    F --> G[Start Step Function]
    
    %% Step Function Workflow
    G --> H[Step Function: ProcessFile]
    H --> I{Check processor-type}
    
    %% Batch Path
    I -->|processor-type = "pool"| J[Submit AWS Batch Job]
    J --> K[Batch Job Queue]
    K --> L[Fargate Compute Environment]
    L --> M[PDF Converter Container]
    
    %% Fargate Path
    I -->|processor-type ≠ "pool"| N[Run ECS Fargate Task]
    N --> O[ECS Cluster]
    O --> P[PDF Converter Container]
    
    %% Container Processing
    M --> Q[Download from S3 Input]
    P --> Q
    Q --> R[Convert Text to PDF]
    R --> S[Upload PDF to S3 Output]
    
    %% Validation and Cleanup
    S --> T[Step Function: Validate Output]
    T --> U{PDF Exists?}
    U -->|Yes| V[Delete SQS Message]
    U -->|No| W[Processing Failed]
    V --> X[Workflow Complete]
    W --> Y[Message Remains in Queue]
    
    %% Dead Letter Queue
    D -.->|Max Retries Exceeded| Z[Dead Letter Queue]
```

## Workflow Components

### 1. **File Upload & Triggering**
- User uploads file to S3 Input Bucket
- S3 sends event notification to SQS Queue
- Lambda function processes SQS messages

### 2. **Orchestration**
- Lambda extracts file metadata and SQS info
- Step Function receives payload with:
  - Source bucket/object
  - Metadata (including processor-type)
  - SQS message details

### 3. **Processing Path Decision**
- **If processor-type = "pool"**: AWS Batch
- **If processor-type ≠ "pool"**: ECS Fargate

### 4. **Container Execution**
- Both paths use same PDF converter container
- Container receives environment variables:
  - `SOURCE_BUCKET`
  - `OBJECT_KEY` 
  - `DEST_BUCKET`

### 5. **File Processing**
- Download text file from S3 Input
- Convert to PDF using ReportLab
- Upload PDF to S3 Output

### 6. **Validation & Cleanup**
- Step Function validates PDF exists
- If successful: Delete SQS message
- If failed: Leave message for retry

### 7. **Error Handling**
- Failed messages retry up to 3 times
- After max retries: Move to Dead Letter Queue

## Key Features
- **Automatic scaling**: Batch and Fargate scale based on demand
- **Fault tolerance**: SQS retry mechanism with DLQ
- **Flexible routing**: Different compute based on metadata
- **Validation**: Ensures processing completed before cleanup
- **Monitoring**: CloudWatch logs for all components

# Architecture

# AWS Architecture Diagram - BatchPoC Workflow

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              BatchPoC File Processing Pipeline                   │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    User     │───▶│  S3 Input   │───▶│ S3 Event    │───▶│ SQS Queue   │
│   Upload    │    │   Bucket    │    │Notification │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                 │
                                                                 ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Dead     │◀───│ SQS Retry   │◀───│   Lambda    │───▶│    Step     │
│Letter Queue │    │ Mechanism   │    │ Processor   │    │ Functions   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                 │
                                                                 ▼
                                      ┌─────────────────────────────────┐
                                      │     Decision: processor-type    │
                                      └─────────────────────────────────┘
                                                 │
                        ┌────────────────────────┼────────────────────────┐
                        ▼                        │                        ▼
              ┌─────────────┐                    │              ┌─────────────┐
              │ AWS Batch   │                    │              │ ECS Fargate │
              │   Queue     │                    │              │   Cluster   │
              └─────────────┘                    │              └─────────────┘
                        │                        │                        │
                        ▼                        │                        ▼
              ┌─────────────┐                    │              ┌─────────────┐
              │  Fargate    │                    │              │  Fargate    │
              │ Compute Env │                    │              │    Task     │
              └─────────────┘                    │              └─────────────┘
                        │                        │                        │
                        └────────────────────────┼────────────────────────┘
                                                 ▼
                                      ┌─────────────────────────────────┐
                                      │     PDF Converter Container     │
                                      │    (ECR Repository Image)       │
                                      └─────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Step     │───▶│   Validate  │───▶│  S3 Output  │───▶│   Delete    │
│ Functions   │    │   Output    │    │   Bucket    │    │ SQS Message │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘

┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ CloudWatch  │    │ CloudWatch  │    │   ECR       │
│   Logs      │    │   Alarms    │    │ Repository  │
└─────────────┘    └─────────────┘    └─────────────┘
```

## AWS Services Used

### **Storage & Data**
- 🪣 **Amazon S3** (Input/Output Buckets)
- 📦 **Amazon ECR** (Container Registry)

### **Compute**
- ⚡ **AWS Lambda** (SQS Message Processing)
- 🔄 **AWS Batch** (Managed Batch Processing)
- 🚀 **Amazon ECS Fargate** (Serverless Containers)

### **Integration & Orchestration**
- 📬 **Amazon SQS** (Message Queue + DLQ)
- 🔀 **AWS Step Functions** (Workflow Orchestration)

### **Monitoring**
- 📊 **Amazon CloudWatch** (Logs & Alarms)

## Architecture Components for Diagram Tools

For creating this diagram in AWS architecture tools (like Lucidchart, Draw.io, or AWS Architecture Icons), use these components:

### **Flow Sequence:**
1. **User/Client** → **S3 Bucket** (Input)
2. **S3 Bucket** → **SQS Queue** (via S3 Event Notifications)
3. **SQS Queue** → **Lambda Function** (Event Source Mapping)
4. **Lambda Function** → **Step Functions** (Start Execution)
5. **Step Functions** → **Decision Diamond** (processor-type check)
6. **Decision** → **AWS Batch** (if "pool") OR **ECS Fargate** (if other)
7. **Both paths** → **Container** (PDF Converter from ECR)
8. **Container** → **S3 Bucket** (Output)
9. **Step Functions** → **Validate Output** → **Delete SQS Message**

### **Supporting Components:**
- **Dead Letter Queue** (connected to main SQS Queue)
- **CloudWatch Logs** (connected to all compute services)
- **CloudWatch Alarms** (monitoring SQS)
- **ECR Repository** (source for container images)

### **Color Coding Suggestion:**
- **Orange**: Storage (S3, ECR)
- **Red**: Messaging (SQS)
- **Yellow**: Compute (Lambda, Batch, ECS)
- **Purple**: Integration (Step Functions)
- **Blue**: Monitoring (CloudWatch)

This structure provides a clear visual representation of how all AWS services interact in your file processing pipeline, showing both the primary workflow and supporting infrastructure components.
