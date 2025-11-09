import json
import boto3
import time
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('StudentProgress')

def lambda_handler(event, context):
    try:
        # Parse request body
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event
        
        # Extract data
        user_id = body.get('userId')
        course_id = body.get('courseId')
        quiz_score = body.get('quizScore')
        
        # Validation
        if not user_id or not course_id or quiz_score is None:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing required fields: userId, courseId, quizScore'
                })
            }
        
        # Create item
        timestamp = int(time.time() * 1000)
        item = {
            'userId': user_id,
            'timestamp': timestamp,
            'courseId': course_id,
            'quizScore': Decimal(str(quiz_score)),
            'completionRate': Decimal(str(body.get('completionRate', 0))),
            'timeSpent': body.get('timeSpent', 0)
        }
        
        # Save to DynamoDB
        table.put_item(Item=item)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Progress recorded successfully',
                'userId': user_id,
                'timestamp': timestamp
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            })
        }