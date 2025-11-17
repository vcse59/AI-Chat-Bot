"""
OpenAI ChatBot Application Entry Point
"""
import uvicorn
import os
from app import app

if __name__ == '__main__':
    # Load configuration from environment variables
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print("=" * 50)
    print("🤖 OpenAI ChatBot API Starting...")
    print("=" * 50)
    print(f"📍 Server: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"🔌 WebSocket: ws://{host}:{port}/ws/chat")
    print("=" * 50)
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY not found!")
        print("   Set it as environment variable for chat functionality")
        print("   Example: export OPENAI_API_KEY=your-key-here")
        print("=" * 50)
    
    uvicorn.run(
        "chat_service.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
