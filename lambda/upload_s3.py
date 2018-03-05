import boto3
import argparse


def upload_file(input_file, bucket_name, object_name):
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(input_file, bucket_name, object_name)
    print("Done")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_file", help="Location of file", required=True)
    parser.add_argument("-o", "--object_name", help="Name of object in bucket", required=True)
    parser.add_argument("-b", "--bucket_name", help="Bucket Name",required=True)

    args = parser.parse_args()

    upload_file(args.input_file, args.bucket_name, args.object_name)



