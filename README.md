# README.md

```markdown
# Conversational AI on AWS
### A Cloud-Based Chat Application with Short-Term Memory
> scalable, observable, production-ready AI systems on AWS.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [AWS Setup](#aws-setup)
- [Deployment](#deployment)
- [Environment Variables](#environment-variables)
- [How Short-Term Memory Works](#how-short-term-memory-works)
- [LLM Providers](#llm-providers)
- [Build Status](#build-status)
- [What Still Needs To Be Built](#what-still-needs-to-be-built)
- [Next Steps](#next-steps)

---

## Project Overview

This project is a cloud-hosted conversational AI chat application
that runs entirely on AWS. Users can have natural, multi-turn
conversations with an AI that remembers what was said earlier
**within the same session** — this is called short-term memory.

When a new session starts, the AI starts fresh with no memory
of previous conversations.

**Who this is for:**
A junior developer with 1–2 years of experience who wants to
understand not just how to build an AI system, but *why* every
piece exists and how they all connect together.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER'S BROWSER                              │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │              Next.js Chat UI (AWS Amplify)                  │  │
│   └────────────────────────────┬────────────────────────────────┘  │
└────────────────────────────────┼────────────────────────────────────┘
                                 │  HTTPS POST /chat
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           AWS CLOUD                                 │
│                                                                     │
│  ┌──────────────────┐     ┌──────────────────────────────────────┐ │
│  │   API Gateway    │────►│         AWS Lambda (Python)          │ │
│  │   (REST API)     │     │                                      │ │
│  └──────────────────┘     │  1. Validate request                 │ │
│                           │  2. Load session from DynamoDB       │ │
│  ┌──────────────────┐     │  3. Trim messages to fit tokens      │ │
│  │  Secrets Manager │◄───►│  4. Build prompt                     │ │
│  │  (API Keys)      │     │  5. Call LLM provider                │ │
│  └──────────────────┘     │  6. Save messages to DynamoDB        │ │
│                           │  7. Return response                  │ │
│  ┌──────────────────┐     └──────────────┬───────────────────────┘ │
│  │    DynamoDB      │◄────────────────────┘                        │
│  │ (Session Memory) │                                              │
│  │  TTL = 24 hours  │     ┌──────────────────────────────────────┐ │
│  └──────────────────┘     │  OpenAI / Anthropic / AWS Bedrock    │ │
│                           └──────────────────────────────────────┘ │
│  ┌──────────────────┐                                              │
│  │   CloudWatch     │  ◄── Logs + Metrics + X-Ray Traces          │
│  └──────────────────┘                                              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Next.js on AWS Amplify | Chat UI, session management |
| API Layer | AWS API Gateway (REST) | Request routing, CORS, rate limiting |
| Business Logic | AWS Lambda (Python 3.12) | AI orchestration, memory management |
| Memory Storage | AWS DynamoDB with TTL | Short-term conversation history |
| LLM Providers | OpenAI / Anthropic / AWS Bedrock | AI response generation |
| Secrets | AWS Secrets Manager | Secure API key storage |
| Observability | AWS CloudWatch + X-Ray | Logging, tracing, debugging |
| Infrastructure | AWS CDK (Python) | All AWS resources defined as code |

---

## Project Structure

```
conversational-ai/
│
├── infrastructure/                    # AWS CDK infrastructure code
│   ├── app.py                         # CDK app entry point
│   ├── requirements.txt               # CDK dependencies
│   └── stacks/
│       ├── dynamodb_stack.py          # DynamoDB table + TTL config
│       ├── lambda_stack.py            # Lambda function + IAM roles
│       ├── api_gateway_stack.py       # REST API + CORS config
│       └── secrets_stack.py           # Secrets Manager setup
│
├── lambda/                            # Lambda function source code
│   ├── handler.py                     # Main Lambda entry point
│   ├── requirements.txt               # Lambda Python dependencies
│   ├── llm/
│   │   ├── client.py                  # LLM API calls + retry logic
│   │   └── prompt_builder.py          # Prompt construction
│   ├── memory/
│   │   └── dynamo_memory.py           # DynamoDB read/write + trimming
│   └── utils/
│       ├── token_counter.py           # Token counting logic
│       └── validators.py              # Request validation
│
├── .env.example                       # Template for environment variables
├── .gitignore
├── Makefile                           # Shortcut commands
└── README.md
```

---

## Prerequisites

Before you begin make sure you have the following installed
and configured on your machine.

### Required Tools

| Tool | Version | Install |
|---|---|---|
| Python | 3.12+ | [python.org](https://python.org) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org) |
| AWS CLI | v2 | [AWS docs](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) |
| AWS CDK | 2.x | `npm install -g aws-cdk` |
| Git | Any | [git-scm.com](https://git-scm.com) |

### Required Accounts

- **AWS Account** with appropriate permissions
- **LLM Provider Account** — at least one of:
  - [OpenAI](https://platform.openai.com) — for GPT models
  - [Anthropic](https://console.anthropic.com) — for Claude models
  - AWS Bedrock — enabled in your AWS account (no separate account needed)

### Required AWS Permissions

Your AWS user or role needs permission to create and manage:

```
- Lambda
- DynamoDB
- API Gateway
- Secrets Manager
- CloudWatch
- X-Ray
- Amplify
- IAM roles and policies
- CDK bootstrap resources (S3, ECR)
```

---

## Local Development Setup
### 1. Clone the repository

```bash
git clone https://github.com/your-username/conversational-ai.git
cd conversational-ai
```

### 2. Configure AWS CLI

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (e.g. us-east-1)
# Enter output format: json
```

Verify it works:

```bash
aws sts get-caller-identity
```

### 3. Install all dependencies

```bash
make install
```

This runs:
- `cd frontend && npm install`
- `cd lambda && pip install -r requirements.txt`
- `cd infrastructure && pip install -r requirements.txt`

### 4. Copy environment variables

```bash
cp .env.example .env.local
```

Open `.env.local` and fill in your values.
See [Environment Variables](#environment-variables) for details.

---

## AWS Setup

### Step 1 — Bootstrap CDK

This only needs to be done once per AWS account and region.
It creates the S3 bucket and roles CDK needs to deploy resources.

```bash
cd infrastructure
cdk bootstrap aws://YOUR_ACCOUNT_ID/YOUR_REGION
```

Replace `YOUR_ACCOUNT_ID` with your 12-digit AWS account number
and `YOUR_REGION` with your region (e.g. `us-east-1`).

### Step 2 — Store your LLM API key in Secrets Manager

Choose the provider you are using and run the matching command.

**OpenAI:**
```bash
aws secretsmanager create-secret \
  --name "chatapp/openai-api-key" \
  --secret-string '{"api_key": "sk-your-openai-key-here"}'
```

**Anthropic:**
```bash
aws secretsmanager create-secret \
  --name "chatapp/anthropic-api-key" \
  --secret-string '{"api_key": "sk-ant-your-anthropic-key-here"}'
```

**AWS Bedrock:**
No API key needed. Bedrock uses your Lambda's IAM role.
You do need to enable model access in the AWS Console:

```
AWS Console → Bedrock → Model Access → Enable your chosen model
```

### Step 3 — Enable Bedrock model access (Bedrock users only)

1. Open the [AWS Console](https://console.aws.amazon.com)
2. Navigate to **Amazon Bedrock**
3. Click **Model Access** in the left sidebar
4. Click **Manage Model Access**
5. Select the model you want (e.g. Claude 3 Haiku)
6. Click **Save Changes**

---

## Deployment

### Deploy all infrastructure

```bash
make deploy-infra
```

This deploys all CDK stacks in order:
1. DynamoDB table with TTL
2. Secrets Manager references
3. Lambda function with IAM role
4. API Gateway with CORS

## Environment Variables

### Lambda — Set in AWS Console or CDK

These are never stored in a file. They live in the Lambda
function's configuration in AWS.

```bash
# Which LLM provider to use
LLM_PROVIDER=openai                    # openai | anthropic | bedrock

# OpenAI settings (if using OpenAI)
OPENAI_SECRET_NAME=chatapp/openai-api-key
OPENAI_MODEL=gpt-4o-mini

# Anthropic settings (if using Anthropic)
ANTHROPIC_SECRET_NAME=chatapp/anthropic-api-key
ANTHROPIC_MODEL=claude-3-5-haiku-20241022

# Bedrock settings (if using Bedrock)
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
BEDROCK_REGION=us-east-1

# Shared LLM settings
MAX_RESPONSE_TOKENS=500
LLM_TEMPERATURE=0.7

# DynamoDB
DYNAMODB_TABLE_NAME=ConversationSessions

```

---

## How Short-Term Memory Works

Each conversation session is stored in DynamoDB as a series
of message records.

```
Session: "sess_abc123"
────────────────────────────────────────────────────
Timestamp               Role        Content
────────────────────────────────────────────────────
2024-01-15T10:00:00Z   user        "What is Python?"
2024-01-15T10:00:01Z   assistant   "Python is a..."
2024-01-15T10:01:00Z   user        "What about Java?"
2024-01-15T10:01:01Z   assistant   "Java is a..."
────────────────────────────────────────────────────
TTL: All records deleted automatically after 24 hours
```

When a new message arrives:
1. All previous messages for the session are loaded from DynamoDB
2. Messages are trimmed to fit within the token limit
3. The trimmed history + new message are sent to the LLM
4. The LLM's response is saved back to DynamoDB
5. The response is returned to the user

**Token trimming strategy:**
- Hard limit: Keep the last 20 messages maximum
- Soft limit: Remove oldest messages until total tokens are under 4,000
- The most recent messages are always kept — they are most relevant

---

## LLM Providers

This project supports three providers. Set `LLM_PROVIDER` in
your Lambda environment to switch between them.

### OpenAI

```bash
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini        # Recommended: fast and affordable
```

Supported models: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`

### Anthropic

```bash
LLM_PROVIDER=anthropic
ANTHROPIC_MODEL=claude-3-5-haiku-20241022    # Recommended: fast
```

Supported models: `claude-3-5-sonnet-20241022`, `claude-3-5-haiku-20241022`

### AWS Bedrock

```bash
LLM_PROVIDER=bedrock
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
BEDROCK_REGION=us-east-1
```

No API key needed — authentication is handled by the Lambda
execution role's IAM policy automatically.

---

## Build Status

| Component | Status | Details |
|---|---|---|
| System Architecture | ✅ Complete | Diagram + component explanations |
| `lambda/memory/dynamo_memory.py` | ✅ Complete | Save, load, trim, format |
| `infrastructure/stacks/dynamodb_stack.py` | ✅ Complete | Table + TTL via CDK |
| `lambda/handler.py` | ✅ Complete | Full orchestration + error handling |
| `lambda/llm/prompt_builder.py` | ✅ Complete | Standard + JSON-structured prompts |
| `lambda/llm/client.py` | ✅ Complete | All three providers + retry logic |
| `lambda/utils/token_counter.py` | ✅ Complete | tiktoken + fallback estimate |
| `lambda/utils/validators.py` | ✅ Complete | Session ID + message validation |
| Project Structure  | ✅ Complete | GitHub-ready layout |
| Frontend — Next.js UI | 🔴 Not started | — |
| Frontend — `useChat` hook | 🔴 Not started | — |
| Frontend — `api.ts` + `session.ts` | 🔴 Not started | — |
| IAM roles + Secrets Manager CDK | 🔴 Not started | — |
| `lambda_stack.py` + `api_gateway_stack.py` | 🔴 Not started | — |
| CloudWatch + X-Ray setup | 🔴 Not started | — |
| Unit + integration tests | 🔴 Not started | — |
| Example conversations | 🔴 Not started | — |

---

## What Still Needs To Be Built

### Frontend
- `frontend/src/app/page.tsx` — main chat page
- `frontend/src/components/ChatWindow.tsx` — chat container
- `frontend/src/components/MessageBubble.tsx` — message display
- `frontend/src/components/MessageInput.tsx` — input + send button
- `frontend/src/hooks/useChat.ts` — state management + API calls
- `frontend/src/lib/api.ts` — API Gateway HTTP client
- `frontend/src/lib/session.ts` — session ID generation + persistence

### Infrastructure
- `infrastructure/stacks/lambda_stack.py` — Lambda + IAM role
- `infrastructure/stacks/api_gateway_stack.py` — REST API + CORS
- `infrastructure/stacks/secrets_stack.py` — Secrets Manager references

### Observability
- CloudWatch log groups and metric filters
- X-Ray tracing configuration
- CloudWatch dashboard for monitoring

---

## Useful Commands

```bash
# Install all dependencies
make install

# Run the frontend locally
make run-frontend

# Run unit tests
make test

# Deploy infrastructure to AWS
make deploy-infra

# Deploy frontend to Amplify
make deploy-frontend

# Tail Lambda logs in real time
make logs

# Tear down all AWS resources
make destroy
```

---

## Troubleshooting

### "Secret not found" error in Lambda logs

The secret name in your environment variable does not match
what you created in Secrets Manager. Check:

```bash
aws secretsmanager list-secrets --query 'SecretList[].Name'
```

### "Access denied" calling Bedrock

The Lambda IAM role is missing the Bedrock permission or
model access has not been enabled in the Bedrock console.
Check both before redeploying.

---

## License

MIT — use this project freely for learning and building.
```