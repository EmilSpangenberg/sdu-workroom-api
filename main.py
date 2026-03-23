"""Compatibility launcher for the modularized API app."""

from app.main import app


if __name__ == "__main__":
    import uvicorn

    print("Starting SDU Workroom Finder API...")
    print("Open http://localhost:8000/docs in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)