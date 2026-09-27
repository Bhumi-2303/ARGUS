import os
import pandas as pd
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from argus.data.manager import data_manager
from argus.schemas.api import TestCaseItem

router = APIRouter()

class SampleResponse(BaseModel):
    id: str
    description: str
    domain: str
    ground_truth_label: int
    ground_truth_class: str
    features: Dict[str, float]


@router.get("/samples", response_model=List[SampleResponse], tags=["data"])
async def get_samples():
    """Discover and return actual verified data samples from parquet files."""
    samples = []
    
    try:
        nfton_path = "data/samples/nfton.parquet"
        ciciot_path = "data/samples/ciciot.parquet"
        
        if os.path.exists(nfton_path):
            df_nf = pd.read_parquet(nfton_path)
            # Take first benign and first attack
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
        pass
        
    return samples


@router.get("/test-cases", response_model=List[TestCaseItem], tags=["data"])
async def get_test_cases():
    """Return the four verified test case rows extracted from source and target test sets."""
    return data_manager.get_test_cases()

