from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import contextlib
import logging

from routers import heritage, ai, admin
from database import engine
from config import settings
from sqlmodel import select, Session
from models import Temple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kalvettu.backend")

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Verify database connection on startup
    try:
        with Session(engine) as session:
            count = len(session.exec(select(Temple.id)).all())
            logger.info(f"Database connection healthy! Verified temples: {count}")
    except Exception as e:
        logger.error(f"Failed to connect to primary database: {e}")
    yield

# Configure interactive docs based on environment
is_prod = settings.ENVIRONMENT.lower() == "production"
docs_url = None if is_prod else "/docs"
redoc_url = None if is_prod else "/redoc"
openapi_url = None if is_prod else "/openapi.json"

app = FastAPI(
    title="Silaimozhi Digital Heritage API",
    description="Authentic epigraphic archive for Tamil temple inscriptions backed by Supabase PostgreSQL & multi-provider AI.",
    version="2.0.0",
    docs_url=docs_url,
    redoc_url=redoc_url,
    openapi_url=openapi_url,
    lifespan=lifespan
)

# 1. Host Header Injection Protection
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# 2. Strict CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# 3. Production Security Headers & Request Body Size Guard Middleware
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    # Enforce request payload size limit (mitigate DoS payload bombs)
    content_length = request.headers.get("content-length")
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if content_length and int(content_length) > max_bytes:
        return JSONResponse(
            status_code=413,
            content={"error": f"Payload exceeds maximum permitted size of {settings.MAX_UPLOAD_SIZE_MB}MB."}
        )

    response = await call_next(request)
    
    # Hardened security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' data: https:; "
        "font-src 'self' https://fonts.gstatic.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;"
    )
    return response

# 4. Safe Global Error Handling (No stack traces or internal secrets leaked to client)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "An internal server error occurred. Please try again later.",
            "path": request.url.path
        }
    )

# 5. Route registration
app.include_router(heritage.router, prefix="/api", tags=["Heritage Data"])
app.include_router(ai.router, prefix="/api/ai", tags=["Kalvettu Intelligence"])
app.include_router(admin.router, prefix="/api/admin", tags=["Administration"])

@app.get("/")
def root():
    return {
        "title": "Silaimozhi – Digital Archive of Tamil Temple Inscriptions",
        "status": "online",
        "version": "2.0.0",
        "archive": "Supabase PostgreSQL & Storage",
        "environment": settings.ENVIRONMENT
    }
