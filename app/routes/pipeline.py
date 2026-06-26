from fastapi import APIRouter
from app.models.requests import PipelineRequest
from app.services.pipeline_service import run_full_pipeline

router = APIRouter()


@router.post("/")
def pipeline_route(request: PipelineRequest):
    return run_full_pipeline(request.image_path)