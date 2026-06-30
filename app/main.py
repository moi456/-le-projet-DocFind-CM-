from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routes import ocr, search

app = FastAPI(
    title="DocFind API",
    description="OCR + Matching + Document Search API",
    version="1.0.0"
)

# setup middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Exposer les images du dataset
app.mount("/data/dataset", StaticFiles(directory="data/dataset"), name="dataset")
# Register routers
app.include_router(ocr.router, prefix="/ocr", tags=["OCR"])
app.include_router(search.router, prefix="/search", tags=["Search"])

@app.get("/")
def root():
    return {
        "message": "DocFind API is running",
        "status": "OK"
    }