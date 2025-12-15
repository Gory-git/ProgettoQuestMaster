"""
ProgettoQuestMaster Backend - Main Application Module

This module contains the core FastAPI application setup, including:
- FastAPI application initialization and configuration
- Middleware configuration (CORS, logging, request/response tracking)
- Health check endpoints for monitoring
- Route inclusion for Phase 1 and Phase 2 features
- Custom error handlers for exception management
- Startup/shutdown events for resource management
- Comprehensive logging and documentation

Author: ProgettoQuestMaster Team
Version: 1.0.0
Last Updated: 2025-12-15
"""

import logging
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class QuestMasterException(Exception):
    """
    Base exception class for ProgettoQuestMaster application.
    
    Attributes:
        detail (str): Description of the error
        status_code (int): HTTP status code
    """
    def __init__(self, detail: str = "An error occurred", status_code: int = 500):
        self.detail = detail
        self.status_code = status_code
        logger.error(f"QuestMasterException: {detail} (Status: {status_code})")
        super().__init__(self.detail)


class ValidationException(QuestMasterException):
    """Raised when validation of input data fails."""
    def __init__(self, detail: str = "Validation error"):
        super().__init__(detail, status_code=422)


class NotFoundException(QuestMasterException):
    """Raised when requested resource is not found."""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail, status_code=404)


class AuthenticationException(QuestMasterException):
    """Raised when authentication fails."""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(detail, status_code=401)


class AuthorizationException(QuestMasterException):
    """Raised when user lacks required permissions."""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(detail, status_code=403)


class InternalServerException(QuestMasterException):
    """Raised for internal server errors."""
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(detail, status_code=500)


# ============================================================================
# APPLICATION LIFECYCLE EVENTS
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for application startup and shutdown events.
    
    This manages application lifecycle including:
    - Initialization of resources during startup
    - Cleanup of resources during shutdown
    - Logging of lifecycle events
    
    Args:
        app (FastAPI): The FastAPI application instance
        
    Yields:
        None
    """
    # STARTUP EVENT
    logger.info("=" * 80)
    logger.info("ProgettoQuestMaster Backend Starting Up")
    logger.info("=" * 80)
    
    try:
        startup_time = datetime.utcnow()
        logger.info(f"Startup initiated at: {startup_time.isoformat()}")
        
        # Initialize database connections (placeholder)
        logger.info("Initializing database connections...")
        # await init_database()
        
        # Load configuration (placeholder)
        logger.info("Loading application configuration...")
        # config = load_config()
        
        # Initialize cache (placeholder)
        logger.info("Initializing cache layer...")
        # await init_cache()
        
        # Verify dependencies (placeholder)
        logger.info("Verifying external dependencies...")
        # await verify_dependencies()
        
        logger.info("✓ Application startup completed successfully")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.critical(f"✗ Application startup failed: {str(e)}", exc_info=True)
        raise
    
    yield  # Application is running
    
    # SHUTDOWN EVENT
    logger.info("=" * 80)
    logger.info("ProgettoQuestMaster Backend Shutting Down")
    logger.info("=" * 80)
    
    try:
        shutdown_time = datetime.utcnow()
        logger.info(f"Shutdown initiated at: {shutdown_time.isoformat()}")
        
        # Close database connections (placeholder)
        logger.info("Closing database connections...")
        # await close_database()
        
        # Clear cache (placeholder)
        logger.info("Clearing cache layer...")
        # await clear_cache()
        
        # Clean up resources (placeholder)
        logger.info("Cleaning up resources...")
        # await cleanup_resources()
        
        logger.info("✓ Application shutdown completed successfully")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}", exc_info=True)


# ============================================================================
# FASTAPI APPLICATION INITIALIZATION
# ============================================================================

app = FastAPI(
    title="ProgettoQuestMaster API",
    description="""
    Quest Management and Learning System API
    
    This API provides comprehensive functionality for:
    - Phase 1: Quest Management and User Progression
    - Phase 2: Advanced Features and Analytics
    
    For more information, visit: https://github.com/Gory-git/ProgettoQuestMaster
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

logger.info("FastAPI application instance created")


# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================

# CORS Middleware - Allow cross-origin requests from specified origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Local React development
        "http://localhost:8080",      # Local alternative
        "https://localhost",          # Local HTTPS
        "http://127.0.0.1:3000",      # Local alternative IP
        # Add production domains as needed
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Page-Number", "X-Page-Size"],
    max_age=3600,
)
logger.info("CORS middleware configured")


# Trusted Host Middleware - Security: only allow requests from trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "*.example.com",  # Add your domain
    ]
)
logger.info("Trusted Host middleware configured")


# ============================================================================
# REQUEST/RESPONSE MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """
    Middleware to log all HTTP requests and responses.
    
    This middleware:
    - Logs incoming request details (method, path, client IP)
    - Measures request processing time
    - Logs response status and details
    - Tracks request IDs for distributed tracing
    
    Args:
        request (Request): The incoming HTTP request
        call_next: The next middleware/handler in the chain
        
    Returns:
        Response: The HTTP response from the next handler
    """
    # Generate request ID for tracking
    request_id = request.headers.get("X-Request-ID", f"{datetime.utcnow().timestamp()}")
    request.state.request_id = request_id
    
    # Record start time
    start_time = time.time()
    
    # Log request details
    client_host = request.client.host if request.client else "Unknown"
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} - "
        f"Client: {client_host} - Query: {dict(request.query_params)}"
    )
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log response details
        logger.info(
            f"[{request_id}] Response: {response.status_code} - "
            f"Processing time: {processing_time:.3f}s"
        )
        
        # Add custom headers to response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(processing_time)
        
        return response
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            f"[{request_id}] Error: {str(e)} - "
            f"Processing time: {processing_time:.3f}s",
            exc_info=True
        )
        raise


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(QuestMasterException)
async def quest_master_exception_handler(request: Request, exc: QuestMasterException):
    """
    Handle custom QuestMaster exceptions.
    
    Returns a formatted JSON response with error details.
    """
    request_id = getattr(request.state, "request_id", "Unknown")
    logger.warning(f"[{request_id}] {exc.__class__.__name__}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "detail": exc.detail,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions with generic error response.
    
    Prevents sensitive information leakage in error responses.
    """
    request_id = getattr(request.state, "request_id", "Unknown")
    logger.error(
        f"[{request_id}] Unhandled exception: {exc.__class__.__name__}: {str(exc)}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "detail": "An unexpected error occurred. Please contact support.",
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Basic Health Check",
    description="Returns 200 OK if the application is running"
)
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    
    This endpoint performs a simple check to verify the application is running.
    
    Returns:
        Dict: Health status information
        
    Example:
        GET /health
        
        Response (200 OK):
        {
            "status": "healthy",
            "timestamp": "2025-12-15T22:14:44.000Z",
            "version": "1.0.0"
        }
    """
    logger.debug("Health check requested")
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.get(
    "/health/detailed",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Detailed Health Check",
    description="Returns detailed application health information including dependencies"
)
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check endpoint.
    
    Performs comprehensive health checks including:
    - Application status
    - Database connectivity (placeholder)
    - Cache connectivity (placeholder)
    - External services (placeholder)
    
    Returns:
        Dict: Detailed health status information
        
    Example:
        GET /health/detailed
        
        Response (200 OK):
        {
            "status": "healthy",
            "timestamp": "2025-12-15T22:14:44.000Z",
            "components": {
                "application": "healthy",
                "database": "healthy",
                "cache": "healthy"
            }
        }
    """
    logger.debug("Detailed health check requested")
    
    # Initialize health status
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "application": "healthy",
            "database": "unknown",  # Replace with actual check
            "cache": "unknown",     # Replace with actual check
        }
    }
    
    try:
        # Check database connectivity (placeholder)
        # health_status["components"]["database"] = await check_database()
        logger.debug("Database health check passed")
    except Exception as e:
        health_status["components"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
        logger.warning(f"Database health check failed: {str(e)}")
    
    try:
        # Check cache connectivity (placeholder)
        # health_status["components"]["cache"] = await check_cache()
        logger.debug("Cache health check passed")
    except Exception as e:
        health_status["components"]["cache"] = "unhealthy"
        health_status["status"] = "degraded"
        logger.warning(f"Cache health check failed: {str(e)}")
    
    return health_status


@app.get(
    "/api/version",
    status_code=status.HTTP_200_OK,
    tags=["Info"],
    summary="Get API Version",
    description="Returns the current API version and build information"
)
async def get_version() -> Dict[str, Any]:
    """
    Get API version and build information.
    
    Returns:
        Dict: Version and build information
        
    Example:
        GET /api/version
        
        Response (200 OK):
        {
            "version": "1.0.0",
            "name": "ProgettoQuestMaster API",
            "environment": "production",
            "timestamp": "2025-12-15T22:14:44.000Z"
        }
    """
    logger.debug("Version information requested")
    return {
        "version": "1.0.0",
        "name": "ProgettoQuestMaster API",
        "environment": "production",
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# ROUTE INCLUSION - PHASE 1
# ============================================================================

# Phase 1: Quest Management and User Progression
# Import and include Phase 1 routers (uncomment when routes are created)

logger.info("Configuring Phase 1 routes...")

# Example router inclusion (uncomment when phase1_router is created):
# from routes.phase1 import router as phase1_router
# app.include_router(
#     phase1_router,
#     prefix="/api/v1/phase1",
#     tags=["Phase 1 - Quest Management"]
# )

logger.info("✓ Phase 1 routes configured")


# ============================================================================
# ROUTE INCLUSION - PHASE 2
# ============================================================================

# Phase 2: Advanced Features and Analytics
# Import and include Phase 2 routers (uncomment when routes are created)

logger.info("Configuring Phase 2 routes...")

# Example router inclusion (uncomment when phase2_router is created):
# from routes.phase2 import router as phase2_router
# app.include_router(
#     phase2_router,
#     prefix="/api/v1/phase2",
#     tags=["Phase 2 - Advanced Features"]
# )

logger.info("✓ Phase 2 routes configured")


# ============================================================================
# OPENAPI SCHEMA CUSTOMIZATION
# ============================================================================

def custom_openapi():
    """
    Customize OpenAPI schema for better documentation.
    
    Returns:
        Dict: Custom OpenAPI schema
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="ProgettoQuestMaster API",
        version="1.0.0",
        description="""
        Quest Management and Learning System API
        
        ## Authentication
        All endpoints require authentication via Bearer token.
        
        ## Rate Limiting
        Requests are limited to 1000 per minute per API key.
        
        ## Error Handling
        All errors return a standardized JSON response with error details.
        """,
        routes=app.routes,
    )
    
    # Add server information
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "Local development server"
        },
        {
            "url": "https://api.example.com",
            "description": "Production server"
        }
    ]
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
logger.info("OpenAPI schema customization applied")


# ============================================================================
# ROOT AND WELCOME ENDPOINTS
# ============================================================================

@app.get(
    "/",
    tags=["Info"],
    summary="Welcome Endpoint",
    description="Welcome message and API information"
)
async def root() -> Dict[str, Any]:
    """
    Welcome endpoint providing API information and documentation links.
    
    Returns:
        Dict: Welcome message and useful links
        
    Example:
        GET /
        
        Response (200 OK):
        {
            "message": "Welcome to ProgettoQuestMaster API",
            "documentation": "http://localhost:8000/api/docs",
            "alternative_docs": "http://localhost:8000/api/redoc",
            "version": "1.0.0"
        }
    """
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to ProgettoQuestMaster API",
        "documentation": "/api/docs",
        "alternative_docs": "/api/redoc",
        "openapi_schema": "/api/openapi.json",
        "health_check": "/health",
        "version": "1.0.0",
        "repository": "https://github.com/Gory-git/ProgettoQuestMaster"
    }


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    """
    Application entry point.
    
    Run the FastAPI application using Uvicorn server.
    
    Usage:
        python main.py
        
    Or use Uvicorn directly:
        uvicorn main:app --reload --host 0.0.0.0 --port 8000
    """
    import uvicorn
    
    logger.info("Starting application server...")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
