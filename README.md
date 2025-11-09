# Real-time Learning Analytics and Automated Intervention System

A serverless learning analytics platform built on AWS that tracks student progress in real-time, predicts at-risk students using machine learning, and automatically alerts instructors.

## 🎯 Features

1. **Real-time Event Tracking** - Captures student learning activities instantly
2. **Predictive At-Risk Detection** - ML-powered student risk assessment
3. **Automated Instructor Alerts** - Email notifications via SNS/SES
4. **Course Analytics** - Aggregate performance statistics

## 🏗️ Architecture

- **API Gateway** - REST API endpoints
- **AWS Lambda** - Serverless compute (Python 3.11)
- **DynamoDB** - NoSQL database with GSI
- **SNS** - Notification service
- **SES** - Email delivery
- **CloudWatch** - Monitoring and logs

## 📊 API Endpoints
```
POST   /progress                              # Record student activity
GET    /analytics/student/{userId}            # Get student risk analysis
GET    /analytics/course/{courseId}           # Get course statistics
```

## 🚀 Deployment

See [DEPLOYMENT.md](documentation/DEPLOYMENT.md) for complete setup instructions.

## 📈 Machine Learning Model

Uses logistic regression to calculate student at-risk probability based on:
- Quiz scores
- Course completion rate
- Time spent on materials

**Risk Formula:**
```
logit = 2.5 + (-0.05 × quiz_score) + (-0.03 × completion_rate) + (-0.0001 × time_spent)
risk_score = 1 / (1 + e^(-logit))
```

Threshold: 0.7 (70% probability triggers alert)

## 🧪 Testing

Import the Postman collection from `/postman` folder for API testing.

## 💰 Cost Estimate

~$19/month for 10,000 students (100 events/student/month)

## 📝 License

MIT License

## 👤 Author

Adithya  Janani 

## 🙏 Acknowledgments

Built as part of learning AWS serverless architecture and ML integration.
