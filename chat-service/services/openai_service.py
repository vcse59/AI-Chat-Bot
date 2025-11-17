import openai
from openai import AsyncOpenAI
from typing import List, Optional, Dict, Any, Sequence
from sqlalchemy.orm import Session
from engine import models, schemas, crud
from engine.database import get_database
from utilities.logging_utils import log_openai_api_call, setup_logger
from utilities.datetime_utils import get_utc_now
import logging

logger = setup_logger(__name__)

class OpenAIConversationService:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """
        Initialize OpenAI conversation service
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-3.5-turbo)
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.default_system_message = "You are a helpful AI assistant."
    
    async def start_conversation(
        self, 
        db: Session, 
        user_id: Optional[str] = None,  # Changed from int to str for hash-based IDs
        title: Optional[str] = None,
        system_message: Optional[str] = None
    ) -> schemas.ConversationResponse:
        """
        Start a new conversation
        
        Args:
            db: Database session
            user_id: Optional user ID
            title: Optional conversation title
            system_message: Optional system message to set context
            
        Returns:
            ConversationResponse: Created conversation
        """
        try:
            # Create conversation
            conversation_data = schemas.ConversationCreate(
                user_id=user_id,
                title=title or "New Conversation",
                metadata={"model": self.model}
            )
            
            conversation = crud.create_conversation(db, conversation=conversation_data)
            
            # Add system message if provided
            if system_message:
                system_msg = schemas.ChatMessageCreate(
                    conversation_id=conversation.id,
                    role=schemas.MessageRole.SYSTEM,
                    content=system_message or self.default_system_message,
                    model=self.model
                )
                crud.create_message(db, message=system_msg)
            
            logger.info(f"Started conversation {conversation.id} for user {user_id}")
            return conversation
            
        except Exception as e:
            logger.error(f"Error starting conversation: {str(e)}")
            raise
    
    async def send_message(
        self,
        db: Session,
        conversation_id: str,  # Changed from int to str for hash-based IDs
        content: str,
        role: schemas.MessageRole = schemas.MessageRole.USER
    ) -> Dict[str, Any]:
        """
        Send a message and get AI response
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            content: Message content
            role: Message role (default: USER)
            
        Returns:
            Dict containing user message and AI response
        """
        try:
            # Verify conversation exists and is active
            conversation = crud.get_conversation(db, conversation_id=conversation_id)
            if not conversation:
                raise ValueError("Conversation not found")
            
            if conversation.status != "active":
                raise ValueError("Conversation is not active")
            
            # Record start time for response time tracking
            start_time = get_utc_now()
            
            # Save user message
            user_message = schemas.ChatMessageCreate(
                conversation_id=conversation_id,
                role=role,
                content=content,
                model=self.model
            )
            saved_user_message = crud.create_message(db, message=user_message)
            
            # Get conversation history for context
            messages = crud.get_conversation_messages(db, conversation_id=conversation_id)
            
            # Prepare messages for OpenAI API
            openai_messages = []
            for msg in messages:
                # Role is already a string in the database, handle both enum and string
                role_str = msg.role.value if hasattr(msg.role, 'value') else msg.role
                openai_messages.append({
                    "role": role_str,
                    "content": msg.content
                })
            
            # Call OpenAI API
            response = await self._call_openai_api(openai_messages)
            
            # Calculate total response time
            end_time = get_utc_now()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Save AI response with response time
            ai_message = schemas.ChatMessageCreate(
                conversation_id=conversation_id,
                role=schemas.MessageRole.ASSISTANT,
                content=response["content"],
                model=self.model,
                tokens_used=response.get("tokens_used"),
                response_time=response_time_ms,
                metadata=response.get("metadata")
            )
            saved_ai_message = crud.create_message(db, message=ai_message)
            
            logger.info(f"Processed message in conversation {conversation_id}")
            
            return {
                "user_message": saved_user_message,
                "ai_response": saved_ai_message,
                "conversation_id": conversation_id,
                "response_time_ms": response_time_ms
            }
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise
    
    async def end_conversation(
        self,
        db: Session,
        conversation_id: str  # Changed from int to str for hash-based IDs
    ) -> schemas.ConversationResponse:
        """
        End a conversation
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            
        Returns:
            ConversationResponse: Updated conversation
        """
        try:
            conversation = crud.end_conversation(db, conversation_id=conversation_id)
            if not conversation:
                raise ValueError("Conversation not found")
            
            logger.info(f"Ended conversation {conversation_id}")
            return conversation
            
        except Exception as e:
            logger.error(f"Error ending conversation: {str(e)}")
            raise
    
    async def get_conversation_context(
        self,
        db: Session,
        conversation_id: str,  # Changed from int to str for hash-based IDs
        limit: int = 10
    ) -> Sequence[schemas.ChatMessageResponse]:  # Changed to Sequence for covariance
        """
        Get recent messages from a conversation for context
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            limit: Number of recent messages to retrieve
            
        Returns:
            Sequence of recent messages
        """
        try:
            messages = crud.get_conversation_messages(
                db, 
                conversation_id=conversation_id, 
                limit=limit
            )
            return messages
            
        except Exception as e:
            logger.error(f"Error getting conversation context: {str(e)}")
            raise
    
    async def _call_openai_api(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Call OpenAI API with error handling and token tracking
        
        Args:
            messages: List of messages for OpenAI API
            
        Returns:
            Dict containing response content and metadata
        """
        try:
            # Record start time for performance logging
            start_time = get_utc_now()
            
            # Use the new OpenAI v1.x API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            # Calculate response time
            end_time = get_utc_now()
            response_time_ms = (end_time - start_time).total_seconds() * 1000
            
            result = {
                "content": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
                "metadata": {
                    "model": self.model,
                    "finish_reason": response.choices[0].finish_reason,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens
                }
            }
            
            # Log successful API call
            log_openai_api_call(
                logger,
                model=self.model,
                tokens_used=response.usage.total_tokens,
                response_time_ms=response_time_ms,
                success=True
            )
            
            return result
            
        except openai.RateLimitError as e:
            error_msg = "API rate limit exceeded. Please try again later."
            log_openai_api_call(logger, model=self.model, success=False, error=error_msg)
            raise ValueError(error_msg)
        
        except openai.BadRequestError as e:
            error_msg = "Invalid request to OpenAI API"
            log_openai_api_call(logger, model=self.model, success=False, error=str(e))
            raise ValueError(error_msg)
        
        except openai.AuthenticationError as e:
            error_msg = "OpenAI API authentication failed"
            log_openai_api_call(logger, model=self.model, success=False, error=str(e))
            raise ValueError(error_msg)
        
        except Exception as e:
            error_msg = f"OpenAI API error: {str(e)}"
            log_openai_api_call(logger, model=self.model, success=False, error=str(e))
            raise ValueError(error_msg)

# Singleton instance
_openai_service = None

def get_openai_service(api_key: str) -> OpenAIConversationService:
    """
    Get or create OpenAI service instance
    
    Args:
        api_key: OpenAI API key
        
    Returns:
        OpenAIConversationService instance
    """
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIConversationService(api_key)
    return _openai_service