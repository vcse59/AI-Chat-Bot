import logging
from typing import Optional
from app.services.chat_service_client import ChatServiceClient

logger = logging.getLogger(__name__)

class LangChainWorkflowService:
        
    def __init__(self, chat_client: ChatServiceClient):
        self.chat_client = chat_client

    async def start_conversation(
            self,
            user_id: str,
            title: Optional[str] = None,
            system_message: Optional[str] = None,
            workflow_type: str = "simple_chain"
        ) -> dict:
            """
            Start a new conversation using chat-service
            """
            metadata = {
                "workflow_type": workflow_type,
                "system_message": system_message
            }
            conversation = await self.chat_client.create_conversation(
                user_id=user_id,
                title=title or f"LangChain Conversation ({workflow_type})",
                metadata=metadata
            )
            return conversation

    async def process_simple_chain(
        self,
        conversation_id: str,
        user_message: str,
        user_id: str,
        system_prompt: Optional[str] = None
    ) -> dict:
        """
        Process user message using chat-service conversation management
        """
        try:
            user_msg = await self.chat_client.create_message(
                conversation_id=conversation_id,
                content=user_message,
                role="user",
                metadata={"workflow_type": "simple_chain", "system_prompt": system_prompt}
            )
            messages = await self.chat_client.get_conversation_messages(conversation_id)
            ai_msg = messages[-1] if messages and messages[-1]["role"] == "assistant" else None
            logger.info(f"Processed simple chain for conversation {conversation_id} using chat-service")
            return {
                "conversation_id": conversation_id,
                "user_message": user_msg,
                "ai_response": ai_msg,
                "workflow_type": "simple_chain"
            }
        except Exception as e:
            logger.error(f"Error in simple chain workflow: {str(e)}")
            raise

    async def process_structured_chain(
        self,
        conversation_id: str,
        user_message: str,
        user_id: str,
        chain_type: str = "qa",
        context: Optional[str] = None
    ) -> dict:
        """
        Process using structured task-specific chains via chat-service
        """
        try:
            user_msg = await self.chat_client.create_message(
                conversation_id=conversation_id,
                content=user_message,
                role="user",
                metadata={"chain_type": chain_type, "context": context}
            )
            messages = await self.chat_client.get_conversation_messages(conversation_id)
            ai_msg = messages[-1] if messages and messages[-1]["role"] == "assistant" else None
            logger.info(f"Processed structured chain ({chain_type}) for conversation {conversation_id} using chat-service")
            return {
                "conversation_id": conversation_id,
                "user_message": user_msg,
                "ai_response": ai_msg,
                "workflow_type": "structured_chain",
                "metadata": {"chain_type": chain_type}
            }
        except Exception as e:
            logger.error(f"Error in structured chain workflow: {str(e)}")
            raise

    async def process_summary_memory(
        self,
        conversation_id: str,
        user_message: str,
        user_id: str
    ) -> dict:
        """
        Process using conversation chain with summary memory via chat-service
        """
        try:
            user_msg = await self.chat_client.create_message(
                conversation_id=conversation_id,
                content=user_message,
                role="user",
                metadata={"workflow_type": "summary_memory"}
            )
            messages = await self.chat_client.get_conversation_messages(conversation_id)
            ai_msg = messages[-1] if messages and messages[-1]["role"] == "assistant" else None
            logger.info(f"Processed summary memory for conversation {conversation_id} using chat-service")
            return {
                "conversation_id": conversation_id,
                "user_message": user_msg,
                "ai_response": ai_msg,
                "workflow_type": "summary_memory"
            }
        except Exception as e:
            logger.error(f"Error in summary memory workflow: {str(e)}")
            raise
