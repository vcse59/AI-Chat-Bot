"""
CRUD operations for MCP Server management
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas
from utilities.hash_utils import generate_hash_id

def create_mcp_server(db: Session, mcp_server: schemas.MCPServerCreate, user_id: str) -> models.MCPServer:
    """Create a new MCP server for a user"""
    # Generate hash-based ID
    server_id = generate_hash_id(prefix="mcp")
    
    db_mcp_server = models.MCPServer(
        id=server_id,
        user_id=user_id,
        name=mcp_server.name,
        description=mcp_server.description,
        server_url=mcp_server.server_url,
        api_key=None,  # Backend uses user's OAuth token for MCP authentication
        auth_type="none",  # Authentication handled by user token
        is_active=mcp_server.is_active,
        config=mcp_server.config
    )
    db.add(db_mcp_server)
    db.commit()
    db.refresh(db_mcp_server)
    return db_mcp_server

def get_mcp_server(db: Session, server_id: str) -> Optional[models.MCPServer]:
    """Get a specific MCP server by ID"""
    return db.query(models.MCPServer).filter(models.MCPServer.id == server_id).first()

def get_user_mcp_servers(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False
) -> List[models.MCPServer]:
    """Get all MCP servers for a specific user"""
    query = db.query(models.MCPServer).filter(models.MCPServer.user_id == user_id)
    
    if active_only:
        query = query.filter(models.MCPServer.is_active == True)
    
    return query.offset(skip).limit(limit).all()

def get_all_mcp_servers(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False
) -> List[models.MCPServer]:
    """Get all MCP servers (admin only)"""
    query = db.query(models.MCPServer)
    
    if active_only:
        query = query.filter(models.MCPServer.is_active == True)
    
    return query.offset(skip).limit(limit).all()

def update_mcp_server(
    db: Session,
    server_id: str,
    mcp_server_update: schemas.MCPServerUpdate
) -> Optional[models.MCPServer]:
    """Update an MCP server"""
    db_mcp_server = get_mcp_server(db, server_id)
    if not db_mcp_server:
        return None
    
    update_data = mcp_server_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_mcp_server, field, value)
    
    db.commit()
    db.refresh(db_mcp_server)
    return db_mcp_server

def delete_mcp_server(db: Session, server_id: str) -> bool:
    """Delete an MCP server"""
    db_mcp_server = get_mcp_server(db, server_id)
    if not db_mcp_server:
        return False
    
    db.delete(db_mcp_server)
    db.commit()
    return True

def count_user_mcp_servers(db: Session, user_id: str, active_only: bool = False) -> int:
    """Count MCP servers for a user"""
    query = db.query(models.MCPServer).filter(models.MCPServer.user_id == user_id)
    
    if active_only:
        query = query.filter(models.MCPServer.is_active == True)
    
    return query.count()
