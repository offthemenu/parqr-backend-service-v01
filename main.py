import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from pathlib import Path
from app.db.session import engine
from app.db.base import Base
from app.routes import car, health_check, parking, user, signup, chat, move_requests, public_profile

load_dotenv(override=True)

# Database URL loaded from environment

app = FastAPI(
    title="parQR API",
    description="Privacy-first parking management API",
    version="1.0.0"
)

# Configure CORS middleware
def get_cors_origins():
    """Generate CORS origins dynamically based on environment"""
    base_origins = [
        "http://localhost:3000",      # React development server
        "http://localhost:19006",     # Expo development server  
        "http://127.0.0.1:3000",
        "http://127.0.0.1:19006",
        "null",                       # For local HTML files
    ]
    
    # Add common development IPs
    dev_ips = [
        "192.168.1.39",   # Current work wifi IP
        "192.0.0.2",      # Phone hotspot IP
    ]
    
    # Add development IPs with common ports
    for ip in dev_ips:
        base_origins.extend([
            f"http://{ip}:19006",    # Expo development server
            f"http://{ip}:8081",     # Metro bundler
            f"exp://{ip}:8081",      # Expo scheme
        ])
    
    return base_origins

origins = get_cors_origins()

# For development: Allow all origins (ONLY for development!)
if os.getenv("DEV_MODE", "false").lower() == "true":
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Servicing QR code images
qr_image_path = Path(__file__).parent / "qr_images"
qr_image_path.mkdir(exist_ok=True)
app.mount("/qr_images", StaticFiles(directory=str(qr_image_path)), name="qr_images")

Base.metadata.create_all(bind=engine)

app.include_router(health_check.router, prefix= "/api")
app.include_router(user.router, prefix= "/api")
app.include_router(car.router, prefix= "/api")
app.include_router(parking.router, prefix= "/api")
app.include_router(signup.router, prefix = "/api")
app.include_router(chat.router, prefix="/api")
app.include_router(public_profile.router, prefix="/api")
app.include_router(move_requests.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        app, 
        host="0.0.0.0",
        port=port,
        log_level="info"
    )