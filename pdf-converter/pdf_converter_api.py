#!/usr/bin/env python3
"""
PDF Converter API Service
Converts text files to PDF and uploads to destination S3 bucket
"""

import boto3
import os
from io import BytesIO
from flask import Flask, request, jsonify
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit

app = Flask(__name__)

def convert_text_to_pdf(text_content):
    """Convert text content to PDF"""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Set up text formatting
    pdf.setFont("Helvetica", 12)
    margin = 50
    line_height = 14
    max_width = width - 2 * margin
    
    # Split text into lines that fit the page width
    lines = []
    for paragraph in text_content.split('\n'):
        if paragraph.strip():
            wrapped_lines = simpleSplit(paragraph, "Helvetica", 12, max_width)
            lines.extend(wrapped_lines)
        else:
            lines.append('')  # Empty line for paragraph breaks
    
    # Write text to PDF
    y_position = height - margin
    for line in lines:
        if y_position < margin:  # Start new page
            pdf.showPage()
            pdf.setFont("Helvetica", 12)
            y_position = height - margin
        
        pdf.drawString(margin, y_position, line)
        y_position -= line_height
    
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()

def process_file(source_bucket, object_key, dest_bucket):
    """Process file from S3: download, convert to PDF, upload"""
    s3 = boto3.client('s3')
    
    try:
        # Download source file
        print(f"Downloading {object_key} from {source_bucket}")
        response = s3.get_object(Bucket=source_bucket, Key=object_key)
        content = response['Body'].read().decode('utf-8')
        
        # Convert to PDF
        print("Converting to PDF...")
        pdf_content = convert_text_to_pdf(content)
        
        # Generate output filename
        base_name = object_key.rsplit('.', 1)[0] if '.' in object_key else object_key
        output_key = f"{base_name}.pdf"
        
        # Upload PDF to destination bucket
        print(f"Uploading {output_key} to {dest_bucket}")
        s3.put_object(
            Bucket=dest_bucket,
            Key=output_key,
            Body=pdf_content,
            ContentType='application/pdf'
        )
        
        print(f"✅ Successfully converted and uploaded {output_key}")
        return output_key
        
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        raise

@app.route('/convert', methods=['POST'])
def convert_pdf():
    """API endpoint to convert text file to PDF"""
    try:
        data = request.get_json()
        source_bucket = data.get('source_bucket')
        object_key = data.get('object_key')
        dest_bucket = data.get('dest_bucket')
        
        if not all([source_bucket, object_key, dest_bucket]):
            return jsonify({
                'error': 'Missing required parameters: source_bucket, object_key, dest_bucket'
            }), 400
        
        output_key = process_file(source_bucket, object_key, dest_bucket)
        
        return jsonify({
            'status': 'success',
            'message': 'Conversion completed',
            'output_key': output_key
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)