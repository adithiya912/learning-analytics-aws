import json
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('StudentProgress')

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    try:
        # Extract courseId from path parameters
        course_id = event.get('pathParameters', {}).get('courseId')
        
        if not course_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'courseId is required'})
            }
        
        # Query using GSI
        response = table.query(
            IndexName='courseId-timestamp-index',
            KeyConditionExpression=Key('courseId').eq(course_id)
        )
        
        items = response.get('Items', [])
        
        if not items:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'No data found for this course'
                })
            }
        
        # Calculate statistics
        total_students = len(set(item['userId'] for item in items))
        avg_score = sum(float(item['quizScore']) for item in items) / len(items)
        avg_completion = sum(float(item.get('completionRate', 0)) for item in items) / len(items)
        avg_time = sum(float(item.get('timeSpent', 0)) for item in items) / len(items)
        
        # Find min/max scores
        scores = [float(item['quizScore']) for item in items]
        min_score = min(scores)
        max_score = max(scores)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'courseId': course_id,
                'total_students': total_students,
                'total_records': len(items),
                'statistics': {
                    'average_score': round(avg_score, 2),
                    'average_completion_rate': round(avg_completion, 2),
                    'average_time_spent': round(avg_time, 2),
                    'min_score': round(min_score, 2),
                    'max_score': round(max_score, 2)
                }
            }, cls=DecimalEncoder)
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
        