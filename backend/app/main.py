import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.firebase import init_firebase
from app.db.sqlalchemy_db import init_sqlalchemy

from app.api.routes import (
    auth,
    patients,
    cases,
    ai,
    analysis,
    posts,
)

# Initialize services & create database tables
init_firebase()
init_sqlalchemy()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Orthodontic AI Analysis Backend API",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://172.23.49.240:5173",
        "http://172.23.49.240:8000",
        "https://orthofinixai.web.app",
        "https://orthofinixai.firebaseapp.com",
        "https://appassets.androidplatform.net",
        "http://localhost",
        "https://localhost",
        "capacitor://localhost",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads folder if missing
os.makedirs("uploads", exist_ok=True)

# Static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth.router, tags=["Auth"])
app.include_router(patients.router, tags=["Patients"])
app.include_router(analysis.router, tags=["Analysis"])
app.include_router(cases.router, tags=["Cases"])
app.include_router(posts.router, tags=["Posts"])
app.include_router(ai.router, tags=["AI"])

from fastapi.responses import FileResponse

# Root endpoint (Health Check)
@app.get("/")
def health_check():
    return {"status": "ok"}

@app.get("/download-apk")
@app.get("/app.apk")
def download_apk():
    apk_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "orthofinixai.apk")
    if not os.path.exists(apk_path):
        apk_path = os.path.abspath("orthofinixai.apk")
    return FileResponse(
        path=apk_path,
        media_type="application/vnd.android.package-archive",
        filename="orthofinixai.apk"
    )

@app.get("/security-review.xlsx")
@app.get("/download-security-excel")
def download_security_excel():
    excel_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "security-review.xlsx")
    if not os.path.exists(excel_path):
        excel_path = os.path.abspath("security-review.xlsx")
    return FileResponse(
        path=excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="security-review.xlsx"
    )

@app.get("/security-review.html")
@app.get("/security-report")
def view_security_html():
    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "security-review.html")
    if not os.path.exists(html_path):
        html_path = os.path.abspath("security-review.html")
    return FileResponse(
        path=html_path,
        media_type="text/html",
        filename="security-review.html"
    )

@app.get("/security-review.md")
def view_security_md():
    md_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "security-review.md")
    if not os.path.exists(md_path):
        md_path = os.path.abspath("security-review.md")
    return FileResponse(
        path=md_path,
        media_type="text/markdown",
        filename="security-review.md"
    )

@app.get("/ping")
def ping():
    return {"ping": "pong"}

@app.get("/warmup")
def warmup():
    """Lightweight endpoint to wake up Render free tier before analysis."""
    return {"status": "warm"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )