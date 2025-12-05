"""
Chat Service Client - Integrates with chat-service OpenAI endpoints
"""
import httpx
from typing import Dict, Any, Optional, List
from app.utils.config import get_settings
from app.utils.logging_utils import setup_logger

logger = setup_logger(__name__)
settings = get_settings()


class ChatServiceClient:
    """
    Client to interact with chat-service OpenAI endpoints
    """
    
    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize chat service client
        
        Args:
            base_url: Base URL of chat service
            token: Authentication token
        """
        self.base_url = base_url or settings.CHAT_SERVICE_URL
        self.token = token
        self.client = httpx.AsyncClient(timeout=60.0)
        
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    async def create_conversation(
        self,
        user_id: str,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new conversation in chat-service
        
        Args:
            user_id: User ID
            title: Conversation title
            metadata: Additional metadata
            
        Returns:
            Conversation data
        """
        try:
            url = f"{self.base_url}/api/v1/users/{user_id}/conversations/"
            payload = {
                "user_id": user_id,
                "title": title or "LangChain Conversation",
                "metadata": metadata or {}
            }
            
            response = await self.client.post(
                url,
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            
            logger.info(f"Created conversation in chat-service: {response.json()['id']}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to create conversation: {str(e)}")
            raise
    
    async def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get conversation details
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation data
        """
        try:
            # Extract user_id from conversation to build proper URL
            # For now, we'll use a direct endpoint if available
            url = f"{self.base_url}/api/v1/conversations/{conversation_id}"
            
            response = await self.client.get(
                url,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get conversation: {str(e)}")
            raise
    
    async def get_conversation_messages(
        self,
        conversation_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get messages from a conversation
        
        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages
            
        Returns:
            List of messages
        """
        try:
            url = f"{self.base_url}/api/v1/conversations/{conversation_id}/messages/"
            params = {"limit": limit}
            
            response = await self.client.get(
                url,
                params=params,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get messages: {str(e)}")
            raise
    
    async def create_message(
        self,
        conversation_id: str,
        content: str,
        role: str = "user",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a message in chat-service
        
        Args:
            conversation_id: Conversation ID
            content: Message content
            role: Message role (user/assistant/system)
            metadata: Additional metadata
            
        Returns:
            Created message data
        """
        try:
            url = f"{self.base_url}/api/v1/conversations/{conversation_id}/messages/"
            payload = {
                "role": role,
                "content": content,
                "model": settings.LANGCHAIN_MODEL,
                "message_metadata": metadata or {}
            }
            
            response = await self.client.post(
                url,
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            
            logger.info(f"Created message in conversation {conversation_id}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to create message: {str(e)}")
            raise
    
    async def health_check(self) -> bool:
        """
        Check if chat service is healthy
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            url = f"{self.base_url}/health"
            response = await self.client.get(url, timeout=5.0)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Chat service health check failed: {str(e)}")
            return False
