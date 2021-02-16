#!/usr/bin/env python3
import os
import json
import urllib3
import datetime
import boto3
from botocore.config import Config

config = Config(
    region_name = 'us-east-2'
)

def s3PutObj(fileName, fileObj, severityResponse):
    print("--- S3 Put Object starts ---")
    print(str(os.environ.get('S3_BUCKET_NAME')) + " - " + str(os.environ.get('S3_OBJECT_KEY')))
    s3Client = boto3.client('s3', config=config)
    
    # s3GetObjResponse = s3Client.get_object(
    #     Bucket="conformitytemplatescannerpublicbucket",
    #     Key="cloudformation-templates/event.json"
    # )
    # print("\n\n"+str(s3GetObjResponse["Body"].read()))
    
    s3PutObjResponse = s3Client.put_object(
        Bucket=str(os.environ.get('S3_BUCKET_NAME')),
        Key=str(os.environ.get('S3_OBJECT_KEY'))+"/"+fileName,
        Body=fileObj
    )
    print(str(s3PutObjResponse))
    
    tempList = []

    for severity in severityResponse.keys():
        tempList.append({'Key': str(severity), 'Value': str(severityResponse[severity])})
    
    s3PutObjTaggingResponse = s3Client.put_object_tagging(
        Bucket=str(os.environ.get('S3_BUCKET_NAME')),
        Key=str(os.environ.get('S3_OBJECT_KEY'))+"/"+fileName,
        Tagging={
            'TagSet': tempList
        }
    )
    print(str(s3PutObjTaggingResponse))
    
def postConformityApi(ccApiKey, fileString):
    headers = {
        "Content-Type": "application/vnd.api+json",
        "Authorization": "ApiKey " + ccApiKey
    }
    data = {
        "data": {
            "attributes": {
                "type": "cloudformation-template",
                "contents": fileString
            }
        }
    }
    http = urllib3.PoolManager()
    r = http.request('POST', 'https://us-west-2-api.cloudconformity.com/v1/template-scanner/scan', headers=headers, body=json.dumps(data))
    responseDict = json.loads(r.data)
    reportDict = {}
    for data in responseDict["data"]:
        if data["type"] == "checks":
            if str(data["attributes"]["risk-level"]) not in reportDict:
                reportDict.update({ data["attributes"]["risk-level"]: 1 })
            else:
                reportDict.update({ data["attributes"]["risk-level"]: reportDict[data["attributes"]["risk-level"]] + 1 })
    print(str(reportDict))
    return reportDict
        
def processJsonFile(ccApiKey, fileName, fileString):
    cfJsonDict = json.loads(fileString)
    if "AWSTemplateFormatVersion" in cfJsonDict:
        ccResponse = postConformityApi(ccApiKey, fileString)
        # print(str(ccResponse))
        s3PutObj(fileName, fileString, ccResponse)
        
def processYamlFile(ccApiKey, fileName, fileString):
    if "AWSTemplateFormatVersion" in fileString:
        ccResponse = postConformityApi(ccApiKey, fileString)
        # print(str(ccResponse))
        s3PutObj(fileName, fileString, ccResponse)

def lambda_handler(event, context):
    ccApiKey = str(os.environ.get('CC_API_KEY'))
    supportedFileExtensions = ["json", "yaml", "yml"]
    print("\nEvent: " + str(event))
    print("\nContext: " + str(context))
    codeCommitClient = boto3.client('codecommit', config=config)
    for record in event["Records"]:
        # print(str(type(record["Sns"]["Message"])))
        print(str(record["Sns"]["Message"]))
        message = json.loads(record["Sns"]["Message"])
        
        codeCommitGetDiffResponse = codeCommitClient.get_differences(
            repositoryName=message["detail"]["repositoryName"],
            beforeCommitSpecifier=message["detail"]["oldCommitId"],
            afterCommitSpecifier=message["detail"]["commitId"]
        )
        # print(str(type(codeCommitGetDiffResponse)))
        print(str(codeCommitGetDiffResponse)) 
        
        for diff in codeCommitGetDiffResponse["differences"]:
            codeCommitGetBlobResponse = codeCommitClient.get_blob(
                repositoryName=message["detail"]["repositoryName"],
                blobId=diff["afterBlob"]["blobId"]
            )
            # print(str(type(codeCommitGetBlobResponse)))
            # print((codeCommitGetBlobResponse["content"]).decode("utf-8"))
            
            if ccApiKey != "" and diff["afterBlob"]["path"].split(".")[-1].lower() in supportedFileExtensions:
                if "afterBlob" in diff:
                    if diff["afterBlob"]["path"].split(".")[-1].lower() == "json":
                        processJsonFile(ccApiKey, diff["afterBlob"]["path"], (codeCommitGetBlobResponse["content"]).decode("utf-8"))
                    elif diff["afterBlob"]["path"].split(".")[-1].lower() == "yaml" or diff["afterBlob"]["path"].split(".")[-1].lower() == "yml":
                        processYamlFile(ccApiKey, diff["afterBlob"]["path"], (codeCommitGetBlobResponse["content"]).decode("utf-8"))
            else:
                print("Not a supported file.")