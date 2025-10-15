import boto3
import random
import os
from datetime import datetime


def generate_lorem_ipsum(word_count=100):
    """Generate random lorem ipsum text"""
    lorem_words = [
        "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit",
        "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore",
        "magna", "aliqua", "enim", "ad", "minim", "veniam", "quis", "nostrud",
        "exercitation", "ullamco", "laboris", "nisi", "aliquip", "ex", "ea", "commodo",
        "consequat", "duis", "aute", "irure", "in", "reprehenderit", "voluptate",
        "velit", "esse", "cillum", "fugiat", "nulla", "pariatur", "excepteur", "sint",
        "occaecat", "cupidatat", "non", "proident", "sunt", "culpa", "qui", "officia",
        "deserunt", "mollit", "anim", "id", "est", "laborum"
    ]
    
    words = [random.choice(lorem_words) for _ in range(word_count)]
    return " ".join(words).capitalize() + "."

    
def lambda_handler(event, context):
    """Lambda function to upload test file to S3 bucket with metadata"""
    
    # Configuration from environment variables
    bucket_name = os.environ.get('BUCKET_NAME', '')
    print(f"output bucket: {bucket_name}")
    
    # Initialize S3 client
    s3 = boto3.client('s3')
    
    # Generate content
    content = generate_lorem_ipsum(150)
    print(f"Generated content: {content}")
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_file_{timestamp}.txt"
    
    # Metadata headers
    metadata = {
        "customer": "AnyCompany",
        "processor-type": "pool",
        "output-destination": "batch-poc-output-bucket-123456789101"
    }
    
    try:
        # Upload file to S3
        upload = s3.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=content.encode('utf-8'),
            ContentType='text/plain',
            Metadata=metadata
        )

        print(upload)
        
        return {
            'statusCode': 200,
            'body': {
                'message': f'Successfully uploaded {filename}',
                'bucket': bucket_name,
                'key': filename,
                'size': len(content),
                'metadata': metadata
            }
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {
                'error': str(e)
            }
        }