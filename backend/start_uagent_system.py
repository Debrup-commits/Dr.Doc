#!/usr/bin/env python3
"""
Startup script for the ASI:One RAG uAgent system
Manages both the uAgent and the Flask API adapter
"""

import os
import sys
import time
import subprocess
import signal
import logging
from typing import List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UAgentSystemManager:
    """Manages the uAgent system components"""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.agent_address: Optional[str] = None
    
    def start_agent(self) -> subprocess.Popen:
        """Start the ASI:One RAG uAgent"""
        logger.info("🚀 Starting ASI:One RAG uAgent...")
        
        # Check if ASI_ONE_API_KEY is set
        if not os.getenv("ASI_ONE_API_KEY"):
            logger.error("❌ ASI_ONE_API_KEY environment variable not set")
            logger.error("Please set your ASI:One API key in the .env file")
            sys.exit(1)
        
        # Start the agent
        process = subprocess.Popen(
            [sys.executable, "asi_one_agent.py"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Monitor the output to get the agent address
        def monitor_agent_output():
            for line in iter(process.stdout.readline, ''):
                print(f"[AGENT] {line.strip()}")
                if "Agent address:" in line:
                    self.agent_address = line.split("Agent address:")[-1].strip()
                    logger.info(f"📍 Agent address: {self.agent_address}")
                elif "Agent ready to process questions" in line:
                    logger.info("✅ ASI:One RAG uAgent is ready")
        
        # Start monitoring in a separate thread
        import threading
        monitor_thread = threading.Thread(target=monitor_agent_output, daemon=True)
        monitor_thread.start()
        
        return process
    
    def start_api(self) -> subprocess.Popen:
        """Start the Flask API adapter"""
        logger.info("🚀 Starting Flask API adapter...")
        
        # Set the agent address if we have it
        if self.agent_address:
            os.environ["AGENT_ADDRESS"] = self.agent_address
        
        process = subprocess.Popen(
            [sys.executable, "app_uagent.py"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Monitor the output
        def monitor_api_output():
            for line in iter(process.stdout.readline, ''):
                print(f"[API] {line.strip()}")
        
        # Start monitoring in a separate thread
        import threading
        monitor_thread = threading.Thread(target=monitor_api_output, daemon=True)
        monitor_thread.start()
        
        return process
    
    def start_system(self):
        """Start the entire system"""
        logger.info("🚀 Starting ASI:One RAG uAgent System...")
        
        try:
            # Start the uAgent
            agent_process = self.start_agent()
            self.processes.append(agent_process)
            
            # Wait a bit for the agent to initialize
            logger.info("⏳ Waiting for agent to initialize...")
            time.sleep(10)
            
            # Start the API
            api_process = self.start_api()
            self.processes.append(api_process)
            
            # Wait a bit for the API to start
            logger.info("⏳ Waiting for API to start...")
            time.sleep(5)
            
            logger.info("✅ System started successfully!")
            logger.info("📍 uAgent: http://localhost:8001")
            logger.info("📍 API: http://localhost:5003")
            logger.info("📍 Web Interface: http://localhost:5003")
            
            if self.agent_address:
                logger.info(f"📍 Agent Address: {self.agent_address}")
            
            # Keep the main process alive
            try:
                while True:
                    time.sleep(1)
                    # Check if any process has died
                    for i, process in enumerate(self.processes):
                        if process.poll() is not None:
                            logger.error(f"❌ Process {i} has died")
                            self.cleanup()
                            sys.exit(1)
            except KeyboardInterrupt:
                logger.info("🛑 Shutting down system...")
                self.cleanup()
                
        except Exception as e:
            logger.error(f"❌ Error starting system: {e}")
            self.cleanup()
            sys.exit(1)
    
    def cleanup(self):
        """Clean up all processes"""
        logger.info("🧹 Cleaning up processes...")
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                logger.warning(f"Error cleaning up process: {e}")
        self.processes.clear()

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("🛑 Received shutdown signal")
    sys.exit(0)

if __name__ == "__main__":
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check if we're in the right directory
    if not os.path.exists("asi_one_agent.py"):
        logger.error("❌ asi_one_agent.py not found. Please run this script from the backend directory.")
        sys.exit(1)
    
    # Start the system
    manager = UAgentSystemManager()
    manager.start_system()


