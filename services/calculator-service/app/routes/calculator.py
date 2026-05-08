from fastapi import APIRouter

from app.schemas.calculator import CalculateResponse, CalculatorRequest
from app.services import calculator as calculator_service

router = APIRouter(prefix="/calculate", tags=["calculator"])


@router.post("", response_model=CalculateResponse)
async def calculate(request: CalculatorRequest) -> CalculateResponse:
    return await calculator_service.calculate(request)
