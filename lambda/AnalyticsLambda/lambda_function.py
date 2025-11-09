import json
import boto3
import math
from decimal import Decimal
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')
table = dynamodb.Table('StudentProgress')

# Replace with your SNS topic ARN
SNS_TOPIC_ARN = 'arn:aws:sns:eu-north-1:YOUR_ACCOUNT_ID:StudentAlertTopic'

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def calculate_risk_score(student_data):
    """Simple logistic regression model for risk prediction"""
    if not student_data:
        return {'is_at_risk': False, 'risk_score': 0.0, 'reason': 'No data available'}
    
    # Calculate features - Convert Decimal to float
    avg_quiz_score = float(sum(float(item['quizScore']) for item in student_data) / len(student_data))
    avg_completion = float(sum(float(item.get('completionRate', 0)) for item in student_data) / len(student_data))
    avg_time_spent = float(sum(float(item.get('timeSpent', 0)) for item in student_data) / len(student_data))
    
    # Logistic regression weights
    intercept = 2.5
    weight_score = -0.05
    weight_completion = -0.03
    weight_time = -0.0001
    
    # Calculate logit
    logit = (intercept + 
             weight_score * avg_quiz_score + 
             weight_completion * avg_completion + 
             weight_time * avg_time_spent)
    
    # Sigmoid function
    risk_score = 1 / (1 + math.exp(-logit))
    
    # Threshold
    is_at_risk = risk_score > 0.7
    
    # Determine reasons
    reasons = []
    if avg_quiz_score < 60:
        reasons.append('Low quiz scores')
    if avg_completion < 50:
        reasons.append('Low completion rate')
    if avg_time_spent < 100:
        reasons.append('Insufficient time spent')
    
    return {
        'is_at_risk': is_at_risk,
        'risk_score': round(risk_score, 2),
        'avg_quiz_score': round(avg_quiz_score, 2),
        'avg_completion_rate': round(avg_completion, 2),
        'avg_time_spent': round(avg_time_spent, 2),
        'reason': ', '.join(reasons) if reasons else 'On track'
    }

def send_alert(user_id, risk_data):
    """Send SNS alert for at-risk student"""
    try:
        message = f"""
STUDENT AT-RISK ALERT

Student ID: {user_id}
Risk Score: {risk_data['risk_score']}
Average Quiz Score: {risk_data['avg_quiz_score']}%
Average Completion: {risk_data['avg_completion_rate']}%
Time Spent: {risk_data['avg_time_spent']} minutes

Reason: {risk_data['reason']}

Please reach out to this student for intervention.
        """
        
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f'At-Risk Student Alert: {user_id}',
            Message=message
        )
        return True
    except Exception as e:
        print(f"Error sending SNS alert: {str(e)}")
        return False

def lambda_handler(event, context):
    try:
        print(f"Received event: {json.dumps(event)}")
        
        # Extract userId from path parameters
        user_id = None
        
        if 'pathParameters' in event and event['pathParameters']:
            user_id = event['pathParameters'].get('userId')
        
        print(f"Extracted userId: {user_id}")
        
        if not user_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'userId is required'
                })
            }
        
        # Query DynamoDB
        response = table.query(
            KeyConditionExpression=Key('userId').eq(user_id)
        )
        
        items = response.get('Items', [])
        print(f"Found {len(items)} records for user {user_id}")
        
        # Calculate risk score
        risk_analysis = calculate_risk_score(items)
        
        # Send alert if at-risk
        if risk_analysis['is_at_risk']:
            alert_sent = send_alert(user_id, risk_analysis)
            risk_analysis['alert_sent'] = alert_sent
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'userId': user_id,
                'total_records': len(items),
                'analytics': risk_analysis
            }, cls=DecimalEncoder)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
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