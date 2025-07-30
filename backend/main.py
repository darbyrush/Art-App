from fastapi import FastAPI
from backend.routers.artworks import router as artworks_router
from backend.routers.feedback import router as feedback_router

app = FastAPI(title="Art API Backend")

# Include the artworks router with /artworks prefix
app.include_router(artworks_router, prefix="/artworks", tags=["Artworks"])

# Include the feedback router with /feedback endpoint
app.include_router(feedback_router, tags=["Feedback"])