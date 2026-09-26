"""Results endpoint."""

from fastapi import APIRouter, HTTPException, status
from argus.schemas.api import ResultTableResponse
from argus.data.manager import data_manager

router = APIRouter()


@router.get("/results/{table}", response_model=ResultTableResponse, tags=["results"])
async def get_result_table(table: str):
    """Serve verified or diagnostic evaluation result tables."""
    try:
        table_res = data_manager.get_result_table(table)
        return table_res
    except KeyError as ke:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Result table '{table}' not found in registry."
        )
    except FileNotFoundError as fnfe:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(fnfe)
        )
