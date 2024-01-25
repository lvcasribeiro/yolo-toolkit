# Imports:
import boto3

# Bucket S3 credentials:
yolo_bucket = boto3.client('s3', aws_access_key_id='AKIA4MG5PQ7GSL7GVDAF', aws_secret_access_key='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')

# Creates a new folder in the s3 bucket:
def create_s3_folder(bucket_name, s3_folder_name):
    try:
        if not s3_folder_name.endswith('/'):
            s3_folder_name += '/'

        yolo_bucket.put_object(Bucket=bucket_name, Key=s3_folder_name)
        
        return True
    except Exception as e:
        return False

# Deletes a folder from the s3 bucket:
def delete_s3_folder(bucket_name, s3_folder_name):
    try:
        if not s3_folder_name.endswith('/'):
            s3_folder_name += '/'

        objects = yolo_bucket.list_objects_v2(Bucket=bucket_name, Prefix=s3_folder_name)
        if 'Contents' in objects:
            for obj in objects['Contents']:
                yolo_bucket.delete_object(Bucket=bucket_name, Key=obj['Key'])

        yolo_bucket.delete_object(Bucket=bucket_name, Key=s3_folder_name)
        
        return True
    except Exception as e:
        return False

# Uploads a new file in the s3 bucket:
def upload_file_to_s3(file, bucket_name, s3_file_name):
    try:
        yolo_bucket.upload_fileobj(file, bucket_name, s3_file_name)

        return True
    except Exception as e:
        return False

# Deletes a file from the s3 bucket:
def delete_file_from_s3(bucket_name, s3_file_name):
    try:
        yolo_bucket.delete_object(Bucket=bucket_name, Key=s3_file_name)
        return True
    except Exception as e:
        return False

# Retrieves the value of an object from the s3 bucket:
def get_file_object_from_s3(bucket_name, s3_file_name):
    try:
        response = yolo_bucket.get_object(Bucket=bucket_name, Key=s3_file_name)
        return response['Body']
    except Exception as e:
        return None

# Retrieves a list of files from a folder of the s3 bucket:
def list_s3_objects(bucket_name, s3_folder_name):
    objects = yolo_bucket.list_objects_v2(Bucket=bucket_name, Prefix=s3_folder_name)
    return [obj['Key'] for obj in objects.get('Contents', [])]
