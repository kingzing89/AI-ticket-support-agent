"""
FastAPI Backend for Support Ticket Agent
Save as: api.py
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from typing import Optional
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.graph import create_support_graph
from src.state import SupportTicketState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Support Ticket Agent API",
    description="AI-powered support ticket resolution system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize graph once at startup
graph = None

@app.on_event("startup")
async def startup_event():
    """Initialize the LangGraph on startup"""
    global graph
    try:
        logger.info("Initializing Support Ticket Agent graph...")
        graph = create_support_graph()
        logger.info("Graph initialized successfully!")
    except Exception as e:
        logger.error(f"Failed to initialize graph: {str(e)}")
        raise


# Request/Response Models
class TicketRequest(BaseModel):
    subject: str
    description: str

class TicketResponse(BaseModel):
    success: bool
    classification: Optional[str] = None
    escalated: bool = False
    review_passed: bool = False
    attempts: int = 1
    final_response: Optional[str] = None
    escalation_message: Optional[str] = None
    error: Optional[str] = None


def create_initial_state(subject: str, description: str) -> SupportTicketState:
    """Create initial state for the graph"""
    return {
        "subject": subject,
        "description": description,
        "classification": None,
        "retrieved_context": None,
        "formatted_context": None,
        "retrieval_attempt": 1,
        "draft_response": None,
        "review_passed": None,
        "reviewer_feedback": None,
        "draft_attempt": 1,
        "max_attempts_reached": None,
        "escalated": None,
    }


@app.post("/api/process-ticket", response_model=TicketResponse)
async def process_ticket(ticket: TicketRequest):
    """
    Process a support ticket through the AI agent
    """
    try:
        logger.info(f"Processing ticket: {ticket.subject}")
        
        # Validate input
        if not ticket.subject.strip() or not ticket.description.strip():
            raise HTTPException(
                status_code=400, 
                detail="Subject and description are required"
            )
        
        # Create initial state
        initial_state = create_initial_state(
            ticket.subject,
            ticket.description
        )
        
        # Run the graph
        final_state = graph.invoke(initial_state)
        
        # Build response
        response = TicketResponse(
            success=True,
            classification=final_state.get('classification'),
            escalated=final_state.get('escalated', False),
            review_passed=final_state.get('review_passed', False),
            attempts=final_state.get('draft_attempt', 1),
            final_response=final_state.get('draft_response'),
            escalation_message=final_state.get('escalation_message')
        )
        
        logger.info(f"Ticket processed successfully: {response.classification}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing ticket: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process ticket: {str(e)}"
        )


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "graph_initialized": graph is not None
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Support Ticket Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from typing import Optional
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.graph import create_support_graph
from src.state import SupportTicketState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Support Ticket Agent API",
    description="AI-powered support ticket resolution system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize graph once at startup
graph = None

@app.on_event("startup")
async def startup_event():
    """Initialize the LangGraph on startup"""
    global graph
    try:
        logger.info("Initializing Support Ticket Agent graph...")
        graph = create_support_graph()
        logger.info("Graph initialized successfully!")
    except Exception as e:
        logger.error(f"Failed to initialize graph: {str(e)}")
        raise


# Request/Response Models
class TicketRequest(BaseModel):
    subject: str
    description: str

class TicketResponse(BaseModel):
    success: bool
    classification: Optional[str] = None
    escalated: bool = False
    review_passed: bool = False
    attempts: int = 1
    final_response: Optional[str] = None
    escalation_message: Optional[str] = None
    error: Optional[str] = None


def create_initial_state(subject: str, description: str) -> SupportTicketState:
    """Create initial state for the graph"""
    return {
        "subject": subject,
        "description": description,
        "classification": None,
        "retrieved_context": None,
        "formatted_context": None,
        "retrieval_attempt": 1,
        "draft_response": None,
        "review_passed": None,
        "reviewer_feedback": None,
        "draft_attempt": 1,
        "max_attempts_reached": None,
        "escalated": None,
    }


@app.post("/api/process-ticket", response_model=TicketResponse)
async def process_ticket(ticket: TicketRequest):
    """
    Process a support ticket through the AI agent
    """
    try:
        logger.info(f"Processing ticket: {ticket.subject}")
        
        # Validate input
        if not ticket.subject.strip() or not ticket.description.strip():
            raise HTTPException(
                status_code=400, 
                detail="Subject and description are required"
            )
        
        # Create initial state
        initial_state = create_initial_state(
            ticket.subject,
            ticket.description
        )
        
        # Run the graph
        final_state = graph.invoke(initial_state)
        
        # Build response
        response = TicketResponse(
            success=True,
            classification=final_state.get('classification'),
            escalated=final_state.get('escalated', False),
            review_passed=final_state.get('review_passed', False),
            attempts=final_state.get('draft_attempt', 1),
            final_response=final_state.get('draft_response'),
            escalation_message=final_state.get('escalation_message')
        )
        
        logger.info(f"Ticket processed successfully: {response.classification}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing ticket: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process ticket: {str(e)}"
        )


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "graph_initialized": graph is not None
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Support Ticket Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from typing import Optional
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.graph import create_support_graph
from src.state import SupportTicketState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Support Ticket Agent API",
    description="AI-powered support ticket resolution system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize graph once at startup
graph = None

@app.on_event("startup")
async def startup_event():
    """Initialize the LangGraph on startup"""
    global graph
    try:
        logger.info("Initializing Support Ticket Agent graph...")
        graph = create_support_graph()
        logger.info("Graph initialized successfully!")
    except Exception as e:
        logger.error(f"Failed to initialize graph: {str(e)}")
        raise


# Request/Response Models
class TicketRequest(BaseModel):
    subject: str
    description: str

class TicketResponse(BaseModel):
    success: bool
    classification: Optional[str] = None
    escalated: bool = False
    review_passed: bool = False
    attempts: int = 1
    final_response: Optional[str] = None
    escalation_message: Optional[str] = None
    error: Optional[str] = None


def create_initial_state(subject: str, description: str) -> SupportTicketState:
    """Create initial state for the graph"""
    return {
        "subject": subject,
        "description": description,
        "classification": None,
        "retrieved_context": None,
        "formatted_context": None,
        "retrieval_attempt": 1,
        "draft_response": None,
        "review_passed": None,
        "reviewer_feedback": None,
        "draft_attempt": 1,
        "max_attempts_reached": None,
        "escalated": None,
    }


@app.post("/api/process-ticket", response_model=TicketResponse)
async def process_ticket(ticket: TicketRequest):
    """
    Process a support ticket through the AI agent
    """
    try:
        logger.info(f"Processing ticket: {ticket.subject}")
        
        # Validate input
        if not ticket.subject.strip() or not ticket.description.strip():
            raise HTTPException(
                status_code=400, 
                detail="Subject and description are required"
            )
        
        # Create initial state
        initial_state = create_initial_state(
            ticket.subject,
            ticket.description
        )
        
        # Run the graph
        final_state = graph.invoke(initial_state)
        
        # Build response
        response = TicketResponse(
            success=True,
            classification=final_state.get('classification'),
            escalated=final_state.get('escalated', False),
            review_passed=final_state.get('review_passed', False),
            attempts=final_state.get('draft_attempt', 1),
            final_response=final_state.get('draft_response'),
            escalation_message=final_state.get('escalation_message')
        )
        
        logger.info(f"Ticket processed successfully: {response.classification}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing ticket: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process ticket: {str(e)}"
        )


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "graph_initialized": graph is not None
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Support Ticket Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from typing import Optional
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.graph import create_support_graph
from src.state import SupportTicketState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Support Ticket Agent API",
    description="AI-powered support ticket resolution system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize graph once at startup
graph = None

@app.on_event("startup")
async def startup_event():
    """Initialize the LangGraph on startup"""
    global graph
    try:
        logger.info("Initializing Support Ticket Agent graph...")
        graph = create_support_graph()
        logger.info("Graph initialized successfully!")
    except Exception as e:
        logger.error(f"Failed to initialize graph: {str(e)}")
        raise


# Request/Response Models
class TicketRequest(BaseModel):
    subject: str
    description: str

class TicketResponse(BaseModel):
    success: bool
    classification: Optional[str] = None
    escalated: bool = False
    review_passed: bool = False
    attempts: int = 1
    final_response: Optional[str] = None
    escalation_message: Optional[str] = None
    error: Optional[str] = None


def create_initial_state(subject: str, description: str) -> SupportTicketState:
    """Create initial state for the graph"""
    return {
        "subject": subject,
        "description": description,
        "classification": None,
        "retrieved_context": None,
        "formatted_context": None,
        "retrieval_attempt": 1,
        "draft_response": None,
        "review_passed": None,
        "reviewer_feedback": None,
        "draft_attempt": 1,
        "max_attempts_reached": None,
        "escalated": None,
    }


@app.post("/api/process-ticket", response_model=TicketResponse)
async def process_ticket(ticket: TicketRequest):
    """
    Process a support ticket through the AI agent
    """
    try:
        logger.info(f"Processing ticket: {ticket.subject}")
        
        # Validate input
        if not ticket.subject.strip() or not ticket.description.strip():
            raise HTTPException(
                status_code=400, 
                detail="Subject and description are required"
            )
        
        # Create initial state
        initial_state = create_initial_state(
            ticket.subject,
            ticket.description
        )
        
        # Run the graph
        final_state = graph.invoke(initial_state)
        
        # Build response
        response = TicketResponse(
            success=True,
            classification=final_state.get('classification'),
            escalated=bool(final_state.get('escalated', False)),
            review_passed=final_state.get('review_passed', False),
            attempts=final_state.get('draft_attempt', 1),
            final_response=final_state.get('draft_response'),
            escalation_message=final_state.get('escalation_message')
        )
        
        logger.info(f"Ticket processed successfully: {response.classification}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing ticket: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process ticket: {str(e)}"
        )


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "graph_initialized": graph is not None
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Support Ticket Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )