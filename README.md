# Trend Micro Cloud One Conformity Scanner for AWS CodeCommit

This AWS CodeCommit repo sets up an integration with AWS CodeCommit and Trend Micro Cloud One Conformity Template Scanner. 

Everytime there is a commit pushed to the configured AWS CodeCommit repo, the commit is parsed for supported file formats (`json`, `yaml`, or `yml`) and checks if the file is an AWS CloudFormation template.

If it is an AWS CloudFormation template, it posts the file to the *Cloud One Conformity Template Scanner API* to retrieve scan results and tag Issues with the scan results on S3 for CodePipeline consumption.

<!-- TODO: Add an AWS Architecture diagram here -->

### Deploy CloudFormation template
---

An AWS CloudFormation template to deploy an AWS Lambda, S3 Bucket and required resources.

### Required fields


 - #### **CC_API_KEY**
        
An API key is required to authenticate requests to the Template Scanner API. You can create an API Key to access Cloud One Conformity APIs by following Conformity documentation provided here - https://www.cloudconformity.com/help/public-api/api-keys.html.
        
> For more information on Cloud One Conformity APIs, please refer to the API reference documentation available here - https://cloudone.trendmicro.com/docs/conformity/api-reference/

 - #### **S3_BUCKET_NAME**

Enter an S3 Bucket Name you would like the scanned CloudFormation templates are tagged and stored onto.

 - #### **S3_OBJECT_KEY**

Enter an S3 Object Key (parent folder) within the selected S3 Bucket.

> The **Outputs** section of the newly created CloudFormation Stack contains the S3 Bucket Name that is used on the AWS Lambda function.

### Cloud One Conformity Template Scanner
---

Lambda function written in Python to configure the AWS CodeCommit repository via AWS CodeCommit APIs -

- Copy files onto S3 Destination Bucket
- Tag Conformity Scan Results as S3 Object Tags

> For more information on AWS CodeCommit APIs, please refer to the API reference documentation available here - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html

### Sample CloudFormation Template
---

The `sample_cloudformation_template.json` file is provided to upload to a configured AWS CodeCommit repository for testing.


## How to deploy
---

- Run the CloudFormation template on AWS. Retrieve the `S3 Bucket Name` from the `Outputs` tab.

- Configure AWS CodeCommit Repository for AWS SNS
    - Navigate to your `AWS CodeCommit Repository > Settings > Notifications`
    - Create a new Notification rule with AWS SNS as Target with `"Updated"` events as triggers for notification
    - Create a new AWS SNS Target topic and click "Submit"

- Configure AWS Lambda Function for AWS SNS  
    - On the AWS Lambda function, ensure the Environment variables as set with `CC_API_KEY`, `S3_BUCKET_NAME`, `S3_OBJECT_KEY`
    - Add a Trigger for the AWS Lambda function and choose the SNS topic we created a few moments ago and ensure "Enable trigger" is `enabled`
    - Click on "Add" to finalize changes to the Lambda function

- Commit the `sample_cloudformation_template.json` to the configured AWS CodeCommit repo.

- Navigate to the AWS S3 Bucket to see the scanned file and the scan results as tags on the file.

- You can now plug in AWS CodePipeline to accept s3::PutObject events to trigger a pipeline build, test for checks (tags) and deploy CloudFormation templates based on Organization's risk acceptance criteria.
    - The supported Cloud One Conformity tags are `EXTREME`, `VERY_HIGH`, `HIGH`, `MEDIUM` and `LOW`