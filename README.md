# Jan Nano 4B Q8 OpenAI Compatible API Cluster

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![AWS](https://img.shields.io/badge/AWS-Cloud-orange.svg)](https://aws.amazon.com)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)

A production-ready OpenAI-compatible API cluster for Jan Nano 4B Q8 model on AWS with load balancing, SSL termination, and automatic scaling.

## 🌟 Features

- **OpenAI Compatible API** - Drop-in replacement for OpenAI API endpoints
- **High Availability** - 3-instance cluster with Application Load Balancer
- **SSL/HTTPS Support** - Automatic SSL certificate management with ACM
- **Custom Domain** - Clean domain access via Route 53
- **Health Monitoring** - Automatic health checks and failover
- **Japanese Language Support** - Optimized for Japanese language processing
- **Auto Deployment** - Complete infrastructure as code

## 🚀 Live Demo

- **HTTP API**: http://jan-nano-api-v2-323468516.ap-northeast-1.elb.amazonaws.com/v1/chat/completions
- **HTTPS API**: https://jan-nano-api.teai.io/v1/chat/completions *(SSL setup in progress)*
- **Health Check**: https://jan-nano-api.teai.io/health

## 📋 Quick Start

### Prerequisites

- AWS CLI configured with appropriate permissions
- Route 53 hosted zone (for custom domain)
- Key pair for EC2 access

### 1. Clone Repository

```bash
git clone https://github.com/yukihamada/jan-nano.git
cd jan-nano
```

### 2. Deploy Infrastructure

```bash
# 1. Create security group
aws ec2 create-security-group --group-name jan-nano-api-sg --description "Jan Nano API security group"

# 2. Deploy instances with API server
aws ec2 run-instances \
  --image-id ami-0d52744d6551d851e \
  --count 3 \
  --instance-type t3.medium \
  --security-group-ids sg-XXXXXXXXX \
  --key-name your-key-name \
  --user-data file://startup.sh

# 3. Create load balancer and configure domain
# See setup_complete_guide.md for detailed steps
```

### 3. Test API

```bash
# Basic health check
curl https://jan-nano-api.teai.io/

# Chat completion
curl -X POST https://jan-nano-api.teai.io/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "jan-nano-4b-q8",
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ],
    "max_tokens": 100
  }'
```

## 🏗 Architecture

```
Internet
    ↓
Route 53 (jan-nano-api.teai.io)
    ↓
Application Load Balancer
    ↓
┌─────────────────────────────────────────┐
│  Target Group (Health Check: /)        │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │ EC2 #1  │ │ EC2 #2  │ │ EC2 #3  │   │
│  │Port 8000│ │Port 8000│ │Port 8000│   │
│  └─────────┘ └─────────┘ └─────────┘   │
└─────────────────────────────────────────┘
```

## 🔧 API Endpoints

### Base URL
```
https://jan-nano-api.teai.io
```

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check and server info |
| GET | `/v1/models` | List available models |
| POST | `/v1/chat/completions` | Chat completion (OpenAI compatible) |

### Chat Completion Example

```bash
curl -X POST https://jan-nano-api.teai.io/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "jan-nano-4b-q8",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "日本語で挨拶してください"}
    ],
    "max_tokens": 150,
    "temperature": 0.7
  }'
```

### Response Format

```json
{
  "id": "chatcmpl-1234567890",
  "object": "chat.completion",
  "created": 1703123456,
  "model": "jan-nano-4b-q8",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "こんにちは！Jan Nano 4B Q8モデルです。"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 15,
    "total_tokens": 35
  }
}
```

## 📁 Project Structure

```
jan-nano/
├── README.md                    # This file
├── setup_complete_guide.md      # Complete deployment guide
├── startup.sh                   # EC2 user data script
├── proven_api.py               # Standalone API server
├── ssl_monitor.py              # SSL certificate monitoring
├── deploy_cluster.sh           # Cluster deployment script
├── test_api.py                 # API testing script
├── test_japanese_complex.py    # Advanced Japanese testing
└── monitoring/
    ├── quick_test.py           # Quick health checks
    └── https_status.md         # HTTPS setup status
```

## 🔍 Monitoring & Testing

### Health Check
```bash
python3 quick_test.py
```

### SSL Certificate Status
```bash
python3 ssl_monitor.py
```

### Advanced Japanese Testing
```bash
python3 test_japanese_complex.py
```

## 💰 Cost Estimation

| Resource | Type | Monthly Cost (USD) |
|----------|------|-------------------|
| EC2 Instances | 3x t3.medium | ~$96 |
| Application Load Balancer | ALB | ~$23 |
| Route 53 | Hosted Zone | $0.50 |
| ACM SSL Certificate | Free | $0 |
| Data Transfer | Variable | ~$10-50 |
| **Total** | | **~$130-170** |

## 🛠 Development

### Local Testing

Run the API server locally for development:

```bash
python3 proven_api.py
# Server starts on http://localhost:8000
```

### Custom Model Integration

To integrate your own model, modify the chat completion handler in `proven_api.py`:

```python
def do_POST(self):
    if self.path == '/v1/chat/completions':
        # Add your custom model logic here
        response_text = your_model.generate(user_input)
```

## 🔐 Security

- Security groups restrict access to necessary ports only
- SSL/TLS encryption for all HTTPS traffic
- Health checks ensure only healthy instances serve traffic
- Load balancer provides DDoS protection

## 📚 Documentation

- [Complete Setup Guide](setup_complete_guide.md) - Detailed deployment instructions
- [HTTPS Status](https_status.md) - SSL certificate setup status
- [API Testing](test_api.py) - Comprehensive API testing suite

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Jan AI](https://jan.ai/) for the base model
- OpenAI for the API specification
- AWS for cloud infrastructure

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yukihamada/jan-nano/issues)
- **API Status**: https://jan-nano-api.teai.io/health
- **Documentation**: [Setup Guide](setup_complete_guide.md)

---

**Live API Endpoint**: https://jan-nano-api.teai.io/v1/chat/completions

Built with ❤️ using AWS, Python, and Claude Code