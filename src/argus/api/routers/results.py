"""Results endpoint with RBAC authorization and path protection."""

from fastapi import APIRouter, HTTPException, status, Depends
from structlog import get_logger

from argus.schemas.api import ResultTableResponse
from argus.data.manager import data_manager
from argus.auth.rbac import require_permission
from argus.auth.models import UserPrincipal

logger = get_logger("argus.api.results")

router = APIRouter()


@router.get("/results/{table}", response_model=ResultTableResponse, tags=["results"])
async def get_result_table(
    table: str,
    user: UserPrincipal = Depends(require_permission("read:results"))
):
    """Serve verified or diagnostic evaluation result tables with RBAC enforcement."""
    try:
        table_res = data_manager.get_result_table(table)
        return table_res
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Result table '{table}' not found in registry."
        )
    except FileNotFoundError:
        logger.error("result_table_missing", table=table)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Result table file not found on disk."
        )
    except Exception as ex:
        logger.error("result_table_read_failed", table=table, error=str(ex), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load requested result table."
        )
