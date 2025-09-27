# ASI:One Full-Stack Deployment Guide

This guide covers deploying both the Next.js frontend and the Fetch.ai uAgent backend for the ASI:One application.

## Project Structure

```
Dr.Doc/
├── src/                    # Next.js frontend
├── backend/               # Fetch.ai uAgent backend
├── package.json          # Frontend dependencies
├── README.md             # Frontend documentation
└── DEPLOYMENT.md         # This file
```

## Backend: Fetch.ai uAgent

### Prerequisites

1. **ASI API Key**: Get your API key from [ASI:One](https://asi1.ai)
2. **Python 3.8+**: Required for uAgents
3. **Git Repository**: For deployment to Render

### Local Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create environment file**:
   ```bash
   cp env.example .env
   ```

3. **Edit .env file** with your ASI API key:
   ```env
   ASI_API_KEY=sk-your-asi-api-key-here
   AGENT_NAME=ASI-One-Agent
   AGENT_SEED=asi-one-agent-seed
   AGENT_PORT=8001
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Test locally**:
   ```bash
   python app.py
   ```

### Deploy to Render

1. **Push to Git repository**:
   ```bash
   git init
   git add .
   git commit -m "Initial uAgent setup"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Create Render Background Worker**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click **+ New** → **Background Worker**
   - Connect your repository
   - Configure:
     - **Environment**: Python
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python app.py`
     - **Environment Variables**: Add `ASI_API_KEY`

3. **Deploy and Monitor**:
   - Click **Create Background Worker**
   - Monitor deployment logs
   - Note the Agent Inspector link from logs

### Connect to Agentverse

1. **Get Agent Inspector Link**:
   - Check Render logs for the Agent Inspector URL
   - Format: `https://agentverse.ai/agent-inspector?agent=<agent-address>`

2. **Connect to Agentverse**:
   - Open the Agent Inspector link
   - Follow the connection process
   - Your agent will appear under "Local Agents"

3. **Test in Agentverse**:
   - Find your agent in the Agentverse interface
   - Start a chat session
   - Test with queries about AI agents and ASI:One

## Frontend: Next.js Application

### Prerequisites

1. **Node.js 18+**: Required for Next.js
2. **Git Repository**: For deployment

### Local Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Run development server**:
   ```bash
   npm run dev
   ```

3. **Open in browser**: [http://localhost:3000](http://localhost:3000)

### Deploy to Vercel (Recommended)

1. **Push to Git repository**:
   ```bash
   git add .
   git commit -m "Add Next.js frontend"
   git push origin main
   ```

2. **Deploy to Vercel**:
   - Go to [Vercel Dashboard](https://vercel.com)
   - Import your Git repository
   - Configure:
     - **Framework Preset**: Next.js
     - **Root Directory**: `.` (root)
     - **Build Command**: `npm run build`
     - **Output Directory**: `.next`

3. **Deploy**:
   - Click **Deploy**
   - Wait for deployment to complete
   - Your app will be available at a Vercel URL

### Alternative: Deploy to Render

1. **Create Web Service**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click **+ New** → **Web Service**
   - Connect your repository
   - Configure:
     - **Environment**: Node
     - **Build Command**: `npm install && npm run build`
     - **Start Command**: `npm start`
     - **Root Directory**: `.`

2. **Deploy**:
   - Click **Create Web Service**
   - Monitor deployment logs
   - Your app will be available at a Render URL

## Integration

### Connect Frontend to Backend

The frontend and backend are designed to work independently:

- **Frontend**: Provides the user interface and documentation
- **Backend**: Provides AI agent capabilities via Agentverse
- **Integration**: Users can interact with the agent through Agentverse

### Testing the Full Stack

1. **Test Frontend**: Verify all pages load correctly
2. **Test Backend**: Verify agent responds in Agentverse
3. **Test Integration**: Use Agentverse to chat with your agent

## Monitoring and Maintenance

### Backend Monitoring

- **Render Logs**: Monitor agent performance and errors
- **Agentverse**: Check agent status and message handling
- **ASI API**: Monitor API usage and credits

### Frontend Monitoring

- **Vercel/Render Logs**: Monitor application performance
- **User Analytics**: Track user engagement
- **Error Tracking**: Monitor for JavaScript errors

## Troubleshooting

### Common Issues

1. **Agent Not Responding**:
   - Check ASI API key validity
   - Verify agent is connected to Agentverse
   - Check Render logs for errors

2. **Frontend Build Failures**:
   - Check Node.js version compatibility
   - Verify all dependencies are installed
   - Check for TypeScript errors

3. **Deployment Issues**:
   - Verify environment variables are set
   - Check build logs for specific errors
   - Ensure repository is properly connected

### Support Resources

- [Fetch.ai Innovation Lab](https://innovationlab.fetch.ai)
- [Agentverse Documentation](https://agentverse.ai/docs)
- [Render Documentation](https://render.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [ASI:One API Documentation](https://api.asi1.ai/docs)

## Next Steps

1. **Enhance Agent Capabilities**:
   - Add more sophisticated prompt engineering
   - Implement memory and context management
   - Add tool integration capabilities

2. **Improve Frontend**:
   - Add real-time chat interface
   - Implement user authentication
   - Add agent management dashboard

3. **Scale and Optimize**:
   - Implement load balancing
   - Add monitoring and alerting
   - Optimize for production performance

## License

This project follows the Fetch.ai Innovation Lab guidelines and ASI:One ecosystem standards.
