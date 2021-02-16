# Trend Micro Cloud One Conformity Scanner for AWS CodeCommit

This GitHub repo sets up an integration with AWS CodeCommit and Trend Micro Cloud One Conformity Template Scanner. 

Everytime there is a commit pushed to the configured AWS CodeCommit repo, the commit is parsed for supported file formats (`json`, `yaml`, or `yml`) and checks if the file is an AWS CloudFormation template.

If it is an AWS CloudFormation template, it posts the file to the *Cloud One Conformity Template Scanner API* to retrieve scan results and store the file in an S3 Bucket, tagging them with the scan results. You could then use the S3 Bucket to setup a CodePipeline pipeline to build, test and deploy CloudFormation resources.

<!-- TODO: Add an AWS Architecture diagram here -->

### Deploy CloudFormation template
---

An AWS CloudFormation template to deploy an AWS Lambda Function, SNS Topic, S3 Bucket and required resources.

### Required fields

 - #### **ConformityApiKey**
        
An API key is required to authenticate requests to the Template Scanner API. You can create an API Key to access Cloud One Conformity APIs by following Conformity documentation provided here - https://www.cloudconformity.com/help/public-api/api-keys.html.
        
> For more information on Cloud One Conformity APIs, please refer to the API reference documentation available here - https://cloudone.trendmicro.com/docs/conformity/api-reference/

 - #### **S3BucketName**

Enter an S3 Bucket Name you would like the scanned CloudFormation templates are tagged and stored onto.

 - #### **S3ObjectKey**

Enter an S3 Object Key (parent folder) within the selected S3 Bucket.

> The **Outputs** section of the newly created CloudFormation Stack contains the S3 Bucket Name, the S3 Object Key path, the ARN of the AWS Lambda function and the SNS Topic used to trigger on CodeCommit updates.

### What the CloudFormation Template automates?

- Create an SNS Topic to trigger the AWS Lambda `ConformityTemplateScanner` Function
- Create a new notification rule with AWS SNS as Target with `"Updated"` events as triggers for notification under the `<Your-AWS-CodeCommit-Repository> > Settings > Notifications`

- Configure AWS Lambda Function for AWS SNS  
    - On the AWS Lambda function, ensure the Environment variables as set with `CC_API_KEY`, `S3_BUCKET_NAME`, `S3_OBJECT_KEY`
- Add an SNS Trigger for the AWS Lambda function
- Create an S3 Bucket to store the scanned CloudFormation templates and their scan results as tags. You can use this S3 Bucket to listen and trigger CodePipeline builds


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

- Run the CloudFormation template on AWS in the same region as the CodeCommit repository. Retrieve the `S3BucketName` from the `Outputs` tab.

- Commit the `sample_cloudformation_template.json` to the configured AWS CodeCommit repo.

- Navigate to the AWS S3 Bucket to see the scanned file and the scan results as tags on the file.

- You can now plug in AWS CodePipeline to accept s3::PutObject events to trigger a pipeline build, test for checks (tags) and deploy CloudFormation templates based on Organization's risk acceptance criteria.
    - The supported Cloud One Conformity tags are `EXTREME`, `VERY_HIGH`, `HIGH`, `MEDIUM` and `LOW`


### Related Projects

| GitHub Repository Name  | Description |
| ------------- | ------------- |
| [cloudOneConformityTemplateScanner](https://github.com/GeorgeDavis-TM/cloudOneConformityTemplateScanner) | Similar to this repository but catered to GitHub Code repositories |

## Contributing

If you encounter a bug or think of a useful feature, or find something confusing in the docs, please
**[Create a New Issue](https://github.com/GeorgeDavis-TM/ConformityTemplateScanner-AWS-CodeCommit/issues/new)**

 **PS.: Make sure to use the [Issue Template](https://github.com/GeorgeDavis-TM/ConformityTemplateScanner-AWS-CodeCommit/tree/master/.github/ISSUE_TEMPLATE)**

We :heart: pull requests. If you'd like to fix a bug or contribute to a feature or simply correct a typo, please feel free to do so.

If you're thinking of adding a new feature, consider opening an issue first to discuss it to ensure it aligns to the direction of the project (and potentially save yourself some time!).