# ASI:One uAgent

![tag:asi-llm-agent](https://img.shields.io/badge/asi-3D8BD3)
![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)

A Fetch.ai uAgent that integrates with ASI:One API for agentic AI capabilities. This agent can be deployed on Agentverse via Render and provides intelligent responses using the ASI:One model.

## Features

- **ASI:One Integration**: Uses the ASI:One API for intelligent responses
- **Chat Protocol**: Implements the standard uAgents chat protocol
- **Agentverse Compatible**: Ready for deployment on Agentverse
- **Mailbox Enabled**: Can receive messages via Agentverse mailbox
- **Error Handling**: Robust error handling and logging

## Project Structure

```
backend/
├── app.py              # Main uAgent application
├── requirements.txt    # Python dependencies
├── env.example        # Environment variables template
└── README.md          # This file
```

## Setup

### 1. Environment Variables

Copy `env.example` to `.env` and fill in your values:

```bash
cp env.example .env
```

Edit `.env`:
```env
ASI_API_KEY=sk-your-asi-api-key-here
AGENT_NAME=ASI-One-Agent
AGENT_SEED=asi-one-agent-seed
AGENT_PORT=8001
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Locally

```bash
python app.py
```

The agent will start and display:
- Agent name and address
- Mailbox connection status
- Agent Inspector link for Agentverse connection

## Deployment on Render

### 1. Prepare Repository

Ensure your repository contains:
- `app.py`
- `requirements.txt`
- `env.example` (optional)
- `README.md`

### 2. Create Background Worker Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **+ New** → **Background Worker**
3. Connect your repository
4. Configure:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Environment Variables**: Add `ASI_API_KEY` with your key value

### 3. Deploy

Click **Create Background Worker** and monitor the deployment logs.

## Agentverse Integration

1. After deployment, check Render logs for the Agent Inspector link
2. Use the link to connect your agent to Agentverse
3. Find your agent under "Local Agents" in Agentverse
4. Start chatting using the Agentverse chat interface

## Usage

The agent responds to various queries about:
- AI agent development
- ASI:One platform features
- Multi-agent systems
- Agentic AI concepts
- Technical guidance for agent building

## Troubleshooting

- **Missing API Key**: Ensure `ASI_API_KEY` is set in Render environment variables
- **Connection Issues**: Check Render logs for mailbox connection status
- **No Responses**: Verify ASI:One API key is valid and has sufficient credits
- **Dependency Errors**: Ensure all packages in `requirements.txt` are compatible

## Development

For local development:
1. Create a virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Set up `.env` file with your ASI API key
4. Run: `python app.py`
5. Use Agent Inspector link to connect to Agentverse

## License

This project is part of the ASI:One ecosystem and follows Fetch.ai Innovation Lab guidelines.
