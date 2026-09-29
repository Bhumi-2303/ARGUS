"""Data exploration and sample retrieval endpoint with RBAC and error logging."""

import os
from typing import List, Dict
import pandas as pd
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from structlog import get_logger

from argus.data.manager import data_manager
from argus.schemas.api import TestCaseItem
from argus.auth.rbac import require_permission
from argus.auth.models import UserPrincipal

logger = get_logger("argus.api.data")

router = APIRouter()


class SampleResponse(BaseModel):
    id: str
    description: str
    domain: str
    ground_truth_label: int
    ground_truth_class: str
    features: Dict[str, float]


@router.get("/samples", response_model=List[SampleResponse], tags=["data"])
async def get_samples(
    user: UserPrincipal = Depends(require_permission("read:telemetry"))
):
    """Discover and return actual verified data samples from parquet files with RBAC enforcement."""
    samples = []

    try:
        nfton_path = "data/samples/nfton.parquet"
        ciciot_path = "data/samples/ciciot.parquet"

        if os.path.exists(nfton_path):
            df_nf = pd.read_parquet(nfton_path)
            for lbl, cname in [(0, "Benign"), (1, "Attack")]:
                subset = df_nf[df_nf["label"] == lbl]
                if not subset.empty:
                    row = subset.iloc[0]
                    samples.append(SampleResponse(
                        id=f"nfton-{cname.lower()}",
                        description=f"NF-ToN-IoT-v2 ({cname} Flow)",
                        domain="nfton",
                        ground_truth_label=lbl,
                        ground_truth_class=cname,
                        features={
                            "pkt_mean_to_max": float(row["pkt_mean_to_max"]),
                            "tcp_flag_density": float(row["tcp_flag_density"]),
                            "log_pkt_mean": float(row["log_pkt_mean"]),
                            "log_pkt_max": float(row["log_pkt_max"])
                        }
                    ))

        if os.path.exists(ciciot_path):
            df_ci = pd.read_parquet(ciciot_path)
            for lbl, cname in [(0, "Benign"), (1, "Attack")]:
                subset = df_ci[df_ci["label"] == lbl]
                if not subset.empty:
                    row = subset.iloc[0]
                    samples.append(SampleResponse(
                        id=f"ciciot-{cname.lower()}",
                        description=f"CICIoT2023 ({cname} Flow)",
                        domain="ciciot",
                        ground_truth_label=lbl,
                        ground_truth_class=cname,
                        features={
                            "pkt_mean_to_max": float(row["pkt_mean_to_max"]),
                            "tcp_flag_density": float(row["tcp_flag_density"]),
                            "log_pkt_mean": float(row["log_pkt_mean"]),
                            "log_pkt_max": float(row["log_pkt_max"])
                        }
                    ))
    except Exception as e:
        logger.error("failed_to_load_samples", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load telemetry samples."
        )

    return samples


@router.get("/test-cases", response_model=List[TestCaseItem], tags=["data"])
async def get_test_cases(
    user: UserPrincipal = Depends(require_permission("read:telemetry"))
):
    """Return verified test case rows extracted from source and target test sets."""
    return data_manager.get_test_cases()
