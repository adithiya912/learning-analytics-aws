# Deployment Guide

Complete step-by-step guide to deploy the Learning Analytics System on AWS.

## Prerequisites

- AWS Account
- AWS CLI configured
- Python 3.11
- Git

## Architecture Diagram
```
User → API Gateway → Lambda Functions → DynamoDB
                ↓
              SNS → SES → Email
```

## Step 1: DynamoDB Setup

Create table `StudentProgress`:
- Partition key: `userId` (String)
- Sort key: `timestamp` (Number)
- GSI: `courseId-timestamp-index`

## Step 2: IAM Role

Create role `LearningAnalyticsLambdaRole` with policies:
- AWSLambdaBasicExecutionRole
- AmazonDynamoDBFullAccess
- AmazonSNSFullAccess
- AmazonSESFullAccess

## Step 3: Lambda Functions

Deploy 3 Lambda functions:
1. IngestLambda
2. AnalyticsLambda
3. CourseAnalyticsLambda

Runtime: Python 3.11
Role: LearningAnalyticsLambdaRole

## Step 4: API Gateway

Create REST API with endpoints:
- POST /progress
- GET /analytics/student/{userId}
- GET /analytics/course/{courseId}

Enable CORS and Lambda Proxy Integration.

## Step 5: SNS & SES

1. Create SNS topic: `StudentAlertTopic`
2. Verify email addresses in SES
3. Update SNS ARN in AnalyticsLambda code

## Testing

Use Postman collection in `/postman` folder.

## Troubleshooting

Check CloudWatch Logs for each Lambda function.