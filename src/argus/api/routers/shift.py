"""Domain shift evaluation endpoint with RBAC, PCA projection, and class-aware CORAL alignment."""

import os
from typing import Dict, Any
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
from sklearn.decomposition import PCA
from fastapi import APIRouter, Query, HTTPException, status, Depends
from structlog import get_logger

from argus.schemas.api import ShiftResponse
from argus.data.manager import data_manager, ALLOWED_DOMAINS, compute_psi
from argus.auth.rbac import require_permission
from argus.auth.models import UserPrincipal
from argus.adaptation.class_aware_coral import ClassAwareCORALAdapter
from argus.registry.model_registry import HARMONIZED_FEATURES

logger = get_logger("argus.api.shift")

router = APIRouter()


@router.get("/shift", response_model=ShiftResponse, tags=["shift"])
async def get_domain_shift(
    domain: str = Query("nfton", description="Target domain: nfton or iec104"),
    window_size: int = Query(
        1000, ge=10, le=50000, description="Rolling window size for statistical shift testing"
    ),
    user: UserPrincipal = Depends(require_permission("read:telemetry")),
):
    """Calculate rolling KS statistic and PSI drift metrics against source domain reference."""
    if domain not in ALLOWED_DOMAINS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid domain '{domain}'. Allowed domains: {sorted(ALLOWED_DOMAINS)}",
        )

    try:
        shift_res = data_manager.calculate_shift(target_domain=domain, window_size=window_size)
        try:
            from argus.observability.metrics import metrics

            for f in shift_res.feature_shifts:
                metrics.record_drift(
                    feature_name=f.feature,
                    domain=domain,
                    ks_statistic=f.ks_statistic,
                    psi_statistic=f.psi_statistic,
                )
        except Exception as mexc:
            logger.warning("metrics_record_drift_failed", error=str(mexc))
        return shift_res
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Telemetry data for domain '{domain}' not found.",
        )
    except Exception as ex:
        logger.error("shift_calculation_failed", domain=domain, error=str(ex), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Domain distribution shift computation failed.",
        )


@router.get("/shift/pca", tags=["shift"])
async def get_shift_pca(
    source_domain: str = Query("ciciot", description="Source reference domain"),
    target_domain: str = Query("nfton", description="Target domain for adaptation"),
    samples: int = Query(
        200, ge=50, le=1000, description="Sample points per domain for 3D visualization"
    ),
    seed: int = Query(42, ge=0, le=2147483647, description="Deterministic seed for sample points"),
    user: UserPrincipal = Depends(require_permission("read:telemetry")),
):
    """Calculate real 3D PCA point clouds and class-aware CORAL alignment transformation matrices."""
    source_path = (
        f"dataset/{source_domain}.parquet"
        if os.path.exists(f"dataset/{source_domain}.parquet")
        else f"data/samples/{source_domain}.parquet"
    )
    target_path = (
        f"dataset/{target_domain}.parquet"
        if os.path.exists(f"dataset/{target_domain}.parquet")
        else f"data/samples/{target_domain}.parquet"
    )

    if not os.path.exists(source_path) or not os.path.exists(target_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data for source '{source_domain}' or target '{target_domain}' not found.",
        )

    try:
        df_source = pd.read_parquet(source_path)
        df_target = pd.read_parquet(target_path)

        # Deterministic sampling
        df_s_sampled = df_source.sample(
            n=min(samples, len(df_source)), random_state=seed
        ).reset_index(drop=True)
        df_t_sampled = df_target.sample(
            n=min(samples, len(df_target)), random_state=seed
        ).reset_index(drop=True)

        X_s = df_s_sampled[HARMONIZED_FEATURES].values.astype(np.float64)
        y_s = (
            df_s_sampled["label"].values.astype(np.int64)
            if "label" in df_s_sampled
            else np.zeros(len(df_s_sampled), dtype=np.int64)
        )

        X_t = df_t_sampled[HARMONIZED_FEATURES].values.astype(np.float64)
        y_t = (
            df_t_sampled["label"].values.astype(np.int64)
            if "label" in df_t_sampled
            else np.zeros(len(df_t_sampled), dtype=np.int64)
        )

        # Real Class-Aware CORAL fitting
        adapter = ClassAwareCORALAdapter(reg=1e-5)
        adapter.fit(X_s, y_s, X_t, y_t)
        X_s_aligned = adapter.transform(X_s, y_s)

        # 3D PCA fitted on joint source and target distribution
        pca = PCA(n_components=3, random_state=seed)
        pca.fit(np.vstack([X_s, X_t]))

        pca_source = pca.transform(X_s)
        pca_target = pca.transform(X_t)
        pca_aligned = pca.transform(X_s_aligned)

        # Calculate empirical KS and PSI before and after alignment
        metrics_before: Dict[str, Any] = {}
        metrics_after: Dict[str, Any] = {}
        ks_b_list, ks_a_list, psi_b_list, psi_a_list = [], [], [], []

        for idx, feat_name in enumerate(HARMONIZED_FEATURES):
            # Before alignment
            ks_res_b = ks_2samp(X_s[:, idx], X_t[:, idx])
            psi_val_b = compute_psi(X_s[:, idx], X_t[:, idx])
            metrics_before[feat_name] = {
                "ks_statistic": round(float(ks_res_b.statistic), 4),
                "ks_pvalue": float(ks_res_b.pvalue),
                "psi_statistic": round(float(psi_val_b), 4),
            }
            ks_b_list.append(ks_res_b.statistic)
            psi_b_list.append(psi_val_b)

            # After alignment
            ks_res_a = ks_2samp(X_s_aligned[:, idx], X_t[:, idx])
            psi_val_a = compute_psi(X_s_aligned[:, idx], X_t[:, idx])
            metrics_after[feat_name] = {
                "ks_statistic": round(float(ks_res_a.statistic), 4),
                "ks_pvalue": float(ks_res_a.pvalue),
                "psi_statistic": round(float(psi_val_a), 4),
            }
            ks_a_list.append(ks_res_a.statistic)
            psi_a_list.append(psi_val_a)

        summary_metrics = {
            "mean_ks_before": round(float(np.mean(ks_b_list)), 4),
            "mean_ks_after": round(float(np.mean(ks_a_list)), 4),
            "mean_psi_before": round(float(np.mean(psi_b_list)), 4),
            "mean_psi_after": round(float(np.mean(psi_a_list)), 4),
            "features_before": metrics_before,
            "features_after": metrics_after,
        }

        # Record drift metrics in OpenTelemetry
        try:
            from argus.observability.metrics import metrics

            for idx, feat_name in enumerate(HARMONIZED_FEATURES):
                metrics.record_drift(
                    feature_name=feat_name,
                    domain=target_domain,
                    ks_statistic=float(ks_b_list[idx]),
                    psi_statistic=float(psi_b_list[idx]),
                )
        except Exception as mexc:
            logger.warning("metrics_record_drift_failed", error=str(mexc))

        # Format real transformation parameters
        transformation_params = {
            "pca_components": pca.components_.tolist(),
            "pca_mean": pca.mean_.tolist(),
            "explained_variance_ratio": [round(float(v), 4) for v in pca.explained_variance_ratio_],
            "class_adapters": {
                str(c): {
                    "A": adapt.A.tolist() if adapt.A is not None else None,
                    "source_mean": adapt.source_mean.tolist()
                    if adapt.source_mean is not None
                    else None,
                    "target_mean": adapt.target_mean.tolist()
                    if adapt.target_mean is not None
                    else None,
                }
                for c, adapt in adapter.adapters.items()
            },
        }

        # Format point arrays for 3D visualization
        source_points = [
            {
                "x": round(float(pt[0]), 3),
                "y": round(float(pt[1]), 3),
                "z": round(float(pt[2]), 3),
                "label": int(y_s[i]),
            }
            for i, pt in enumerate(pca_source)
        ]
        target_points = [
            {
                "x": round(float(pt[0]), 3),
                "y": round(float(pt[1]), 3),
                "z": round(float(pt[2]), 3),
                "label": int(y_t[i]),
            }
            for i, pt in enumerate(pca_target)
        ]
        aligned_points = [
            {
                "x": round(float(pt[0]), 3),
                "y": round(float(pt[1]), 3),
                "z": round(float(pt[2]), 3),
                "label": int(y_s[i]),
            }
            for i, pt in enumerate(pca_aligned)
        ]

        return {
            "source_domain": source_domain,
            "target_domain": target_domain,
            "sample_count": len(source_points),
            "source_points": source_points,
            "target_points": target_points,
            "aligned_points": aligned_points,
            "metrics": summary_metrics,
            "transformation": transformation_params,
        }

    except Exception as ex:
        logger.error("pca_shift_computation_failed", error=str(ex), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compute PCA domain shift: {str(ex)}",
        )
