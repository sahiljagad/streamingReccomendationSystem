from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import auth, user, content

# Create FastAPI app
app = FastAPI(
    title="Streaming Recommender API",
    description="Personalized streaming recommendations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/")
def root():
    return {"message": "Streaming Recommender API", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/api/user", tags=["User"])
app.include_router(content.router, prefix="/api/content", tags=["Content"])