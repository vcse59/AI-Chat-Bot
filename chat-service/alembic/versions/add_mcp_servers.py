"""Add MCP servers table

Revision ID: add_mcp_servers
Revises: 
Create Date: 2025-11-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers
revision = 'add_mcp_servers'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create mcp_servers table"""
    op.create_table(
        'mcp_servers',
        sa.Column('id', sa.String(length=12), nullable=False),
        sa.Column('user_id', sa.String(length=16), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('server_url', sa.String(length=500), nullable=False),
        sa.Column('api_key', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mcp_servers_id'), 'mcp_servers', ['id'], unique=False)


def downgrade():
    """Drop mcp_servers table"""
    op.drop_index(op.f('ix_mcp_servers_id'), table_name='mcp_servers')
    op.drop_table('mcp_servers')
