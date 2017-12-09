from boto3.session import Session
import botocore
import sys
import os
from os import getcwd
from os import listdir
from os.path import isfile, join
import subprocess
import string


# More info about transfer progress: http://boto3.readthedocs.io/en/latest/_modules/boto3/s3/transfer.html
ENCRYPT_PROGRAM_PATH = "ENTER YOUR PATH TO GO ENCRYPTION"
ACCESS_KEY = "ENTER YOUR AWS ACCESS KEY"
SECRET_KEY = "ENTER YOUR AWS SECRET KEY"
BUCKET_NAME = "ENTER THE NAME OF YOUR AWS BUCKET"

#Connect to bucket
session = Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
s3 = session.resource('s3')
my_bucket = s3.Bucket(BUCKET_NAME)


#Check arguments
file_args = sys.argv
arg_count = len(file_args)
if arg_count < 2 or arg_count > 3:
    print("Invalid number arguments.")
    exit(0)

file_name = ''
if arg_count == 3:
    file_name = file_args[2]


def list_files_on_server():
    count = 0
    for s3_file in my_bucket.objects.all():
        count += 1
    if count == 0:
        print("No files on server.")
        return
    print("%-50s    %s" % ("File", "Size"))
    print("------------------------------------------------------------")
    for s3_file in my_bucket.objects.all():
        count += 1
        size = s3_file.size / (1024)
        print("%-50s %5.3fKB" % (s3_file.key, size))


def encrypt():
    file_extension = file_name[-4:]
    if file_extension != ".enc":
        if os.path.isfile(file_name):
            subprocess.run([ENCRYPT_PROGRAM_PATH, file_name])
        else:
            print("File does not exist.")
            return False
    else:
        print("File is already encrypted.\n")


def decrypt():
    file_extension = file_name[-4:]
    if file_extension == ".enc":
        if os.path.isfile(file_name):
            subprocess.run([ENCRYPT_PROGRAM_PATH, file_name])
        else:
            print("File does not exist.")
            return False
    else:
        print("File must be encrypted and have \".enc\" as file extension.")


def upload():
    upload_file_name = file_name
    if file_args[1] == "eu":
        upload_file_name = file_args[2] + ".enc"
    elif file_args[1] == "u":
        upload_file_name = file_args[2]

    if os.path.isfile(upload_file_name):
        file = open(upload_file_name, 'rb')
    else:
        print("\nFile does not exist.\n")
        return False

    try:
        s3.Bucket(BUCKET_NAME).put_object(Key=upload_file_name, Body=file)
        print("%s uploaded." % upload_file_name)
    except:
        print("\nUnable to upload to bucket.\n")


def download_file():
    try:
        s3.Bucket(BUCKET_NAME).download_file(file_name, file_name)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("%s does not exist on server." % file_name)
            return
    print("%s downloaded." % file_name)


def delete_from_server():
    try:
        s3.Object(BUCKET_NAME, file_name).delete()
    except:
        print("%s does not exist on server." % file_name)
        return

    print("%s deleted." % file_name)


def encrypt_upload():
    encrypt()
    upload()
    # Remove encrypted file when user requested to encrypt and upload
    os.remove(file_name + ".enc")


def invalid():
    print("Invalid request.")
    exit(0)


# Dictionary of different requests and their appropriate functions
request_dict = {
    "list": list_files_on_server,
    "eu": encrypt_upload,
    "u": upload,
    "e": encrypt,
    "d": decrypt,
    "del": delete_from_server,
    "down": download_file
    }

request = file_args[1]
# Grabs function to call from request_dict
# Uses 'invalid' function if invalid request
function_to_call = request_dict.get(request, invalid)
function_to_call()
