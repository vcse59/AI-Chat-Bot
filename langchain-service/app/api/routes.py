"""
FastAPI routes for LangChain Workflow Service
"""
from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Optional

from app.models.schemas import (
    ConversationStartRequest,
    MessageRequest,
    StructuredMessageRequest,
    WorkflowResponse,
    ConversationSummaryResponse
)
from app.services.langchain_workflow import LangChainWorkflowService
from app.services.chat_service_client import ChatServiceClient
from app.utils.logging_utils import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


from fastapi import Request

def get_workflow_service(authorization: Optional[str] = Header(None)) -> LangChainWorkflowService:
    """
    Dependency to get LangChain workflow service with auth token
    Args:
        authorization: Authorization header
    Returns:
        LangChainWorkflowService instance
    """
    token = ""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
    chat_client = ChatServiceClient(token=token)
    service = LangChainWorkflowService(chat_client)
    return service


# Workflow creation endpoint for frontend template
@router.post("/workflows", tags=["workflows"])
async def create_workflow(
    request: Request,
    service: LangChainWorkflowService = Depends(get_workflow_service)
):
    """
    Create a new LangChain workflow from frontend template
    Expects JSON body with workflow configuration (user_id, title, system_message, workflow_type)
    """
    try:
        data = await request.json()
        user_id = data.get("user_id", "anonymous")
        title = data.get("title")
        system_message = data.get("system_message")
        workflow_type = data.get("workflow_type", "simple_chain")
        conversation = await service.start_conversation(
            user_id=user_id,
            title=title,
            system_message=system_message,
            workflow_type=workflow_type
        )
        return {"success": True, "conversation": conversation}
    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversations/start", tags=["conversations"])
async def start_conversation(
    request: ConversationStartRequest,
    service: LangChainWorkflowService = Depends(get_workflow_service)
):
    """
    Start a new conversation with LangChain workflow
    
    **Workflow Types:**
    - `simple_chain`: Basic conversation with full memory
    - `structured_chain`: Task-specific chains (Q&A, summarization, extraction)
    - `summary_memory`: Long conversations with automatic summarization
    """
    try:
        conversation = await service.start_conversation(
            user_id=request.user_id or "anonymous",
            title=request.title,
            system_message=request.system_message,
            workflow_type=request.workflow_type
        )
        return {"success": True, "conversation": conversation}
    except Exception as e:
        logger.error(f"Error starting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversations/{conversation_id}/message/simple", response_model=WorkflowResponse, tags=["messages"])
async def send_message_simple_chain(
    conversation_id: str,
    request: MessageRequest,
    service: LangChainWorkflowService = Depends(get_workflow_service)
):
    """
    Send a message using simple conversation chain with memory
    
    This endpoint uses LangChain's ConversationChain with buffer memory
    to maintain full context across messages.
    
    **Best for:** General conversations up to 50 messages
    """
    try:
        result = await service.process_simple_chain(
            conversation_id=conversation_id,
            user_message=request.message,
            user_id="user",  # Will be extracted from token in production
            system_prompt=request.system_prompt
        )
        return result
    except Exception as e:
        logger.error(f"Error processing simple chain: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversations/{conversation_id}/message/structured", response_model=WorkflowResponse, tags=["messages"])
async def send_message_structured_chain(
    conversation_id: str,
    request: StructuredMessageRequest,
    service: LangChainWorkflowService = Depends(get_workflow_service)
):
    """
    Send a message using structured task-specific chains
    
    **Chain Types:**
    - `qa`: Question answering with context
    - `summarize`: Text summarization
    - `extract`: Information extraction
    
    **Best for:** Specific tasks with provided context
    """
    try:
        result = await service.process_structured_chain(
            conversation_id=conversation_id,
            user_message=request.message,
            user_id="user",
            chain_type=request.chain_type,
            context=request.context
        )
        return result
    except Exception as e:
        logger.error(f"Error processing structured chain: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversations/{conversation_id}/message/summary-memory", response_model=WorkflowResponse, tags=["messages"])
async def send_message_summary_memory(
    conversation_id: str,
    request: MessageRequest,
    service: LangChainWorkflowService = Depends(get_workflow_service)
):
    """
    Send a message using conversation chain with summary memory
    
    This workflow automatically summarizes conversation history to reduce
    token usage while maintaining context.
    
    **Best for:** Long conversations with 50+ messages
    """
    try:
        result = await service.process_summary_memory(
            conversation_id=conversation_id,
            user_message=request.message,
            user_id="user"
        )
        return result
    except Exception as e:
        logger.error(f"Error processing summary memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


