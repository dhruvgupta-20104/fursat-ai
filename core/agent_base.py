# core/agent_base.py

from abc import ABC, abstractmethod
import logging
from typing import Dict, Any
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(name)
        
    @abstractmethod
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming messages and return response."""
        pass
    
    def log_activity(self, activity: str):
        """Log agent activity with timestamp."""
        self.logger.info(f"[{self.name}] {activity}")

class AgentRouter:
    """Routes messages to appropriate agents based on message type and content."""
    
    def __init__(self):
        self.agents = {}
        self.logger = logging.getLogger("AgentRouter")
    
    def register_agent(self, message_type: str, agent: BaseAgent):
        """Register an agent to handle specific message types."""
        self.agents[message_type] = agent
        self.logger.info(f"Registered agent {agent.name} for message type {message_type}")
    
    async def route_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Route message to appropriate agent and return response."""
        message_type = message.get("type", "default")
        
        if message_type in self.agents:
            agent = self.agents[message_type]
            agent.log_activity(f"Processing message: {message}")
            return await agent.process_message(message)
        else:
            self.logger.warning(f"No agent registered for message type: {message_type}")
            return {"error": "No agent available for this message type"}