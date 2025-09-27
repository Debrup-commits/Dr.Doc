#!/usr/bin/env python3
"""
Startup script for the Agentic Document Q&A System
Starts both the uAgent and the API adapter
"""

import os
import sys
import time
import signal
import subprocess
import threading
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AgenticSystemManager:
    """Manages the agentic document Q&A system"""
    
    def __init__(self):
        self.agent_process = None
        self.api_process = None
        self.running = False
        
    def start_agent(self):
        """Start the Document Q&A uAgent"""
        print("🤖 Starting Document Q&A uAgent...")
        
        try:
            # Start the agent process
            self.agent_process = subprocess.Popen([
                sys.executable, "doc_qa_agent.py"
            ], cwd=Path(__file__).parent)
            
            print("✅ uAgent started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start uAgent: {e}")
            return False
    
    def start_api_adapter(self):
        """Start the API adapter"""
        print("🌐 Starting API Adapter...")
        
        # Wait a bit for the agent to initialize
        time.sleep(5)
        
        try:
            # Start the API adapter process
            self.api_process = subprocess.Popen([
                sys.executable, "agent_api_adapter.py"
            ], cwd=Path(__file__).parent)
            
            print("✅ API Adapter started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start API Adapter: {e}")
            return False
    
    def stop_system(self):
        """Stop the entire system"""
        print("\n🛑 Stopping Agentic Document Q&A System...")
        self.running = False
        
        if self.api_process:
            print("🛑 Stopping API Adapter...")
            self.api_process.terminate()
            self.api_process.wait()
        
        if self.agent_process:
            print("🛑 Stopping uAgent...")
            self.agent_process.terminate()
            self.agent_process.wait()
        
        print("✅ System stopped successfully")
    
    def monitor_processes(self):
        """Monitor the running processes"""
        while self.running:
            try:
                # Check agent process
                if self.agent_process and self.agent_process.poll() is not None:
                    print("⚠️ uAgent process has stopped unexpectedly")
                    self.running = False
                    break
                
                # Check API process
                if self.api_process and self.api_process.poll() is not None:
                    print("⚠️ API Adapter process has stopped unexpectedly")
                    self.running = False
                    break
                
                time.sleep(2)
                
            except KeyboardInterrupt:
                break
    
    def run(self):
        """Run the complete system"""
        print("🚀 Starting Agentic Document Q&A System")
        print("=" * 60)
        
        # Set up signal handlers
        def signal_handler(signum, frame):
            self.stop_system()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # Start the uAgent
            if not self.start_agent():
                print("❌ Failed to start uAgent. Exiting.")
                return
            
            # Start the API adapter
            if not self.start_api_adapter():
                print("❌ Failed to start API Adapter. Stopping uAgent.")
                self.stop_system()
                return
            
            self.running = True
            
            print("\n🎉 Agentic Document Q&A System is running!")
            print("📍 API available at: http://localhost:5003")
            print("🤖 uAgent running on port: 8001")
            print("🔗 Agent inspector will be available after agent initialization")
            print("🛑 Press Ctrl+C to stop the system")
            print("=" * 60)
            
            # Monitor processes
            self.monitor_processes()
            
        except Exception as e:
            print(f"❌ System error: {e}")
            self.stop_system()

def main():
    """Main function"""
    manager = AgenticSystemManager()
    manager.run()

if __name__ == "__main__":
    main()
