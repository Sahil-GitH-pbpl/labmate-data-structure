from fastapi import APIRouter

from ..schemas import HealthResponse

router = APIRouter(prefix="/infra", tags=["health"])


@router.get("/healthz", response_model=HealthResponse)
async def healthcheck():
    return HealthResponse()
