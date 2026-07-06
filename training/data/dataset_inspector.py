import pandas as pd
from typing import Dict, Any, Tuple

from training.utils.logger import get_logger

class DatasetInspector:
    """Inspects DataFrames and generates summary statistics (does not load files)."""
    
    def __init__(self):
        """Initializes the DatasetInspector."""
        self.logger = get_logger(__name__)

    def inspect(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generates basic summary statistics for numeric columns.
        
        Args:
            df: The DataFrame to inspect.
            
        Returns:
            dict: Summary statistics suitable for JSON serialization.
        """
        self.logger.info("inspecting_dataset", shape=df.shape)
        # Using describe() and converting to dict, replacing NaNs with None for JSON compat
        stats = df.describe().replace({pd.NA: None}).to_dict()
        return stats

    def get_dtypes(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Returns a mapping of column names to their string data types.
        """
        return {col: str(dtype) for col, dtype in df.dtypes.items()}

    def get_missing_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculates missing value counts and percentages per column.
        """
        missing_counts = df.isnull().sum()
        missing_pct = (missing_counts / len(df)) * 100
        
        summary = {}
        for col in df.columns:
            if missing_counts[col] > 0:
                summary[col] = {
                    "count": int(missing_counts[col]),
                    "percentage": float(round(missing_pct[col], 2))
                }
        return summary

    def get_class_distribution(self, df: pd.DataFrame, target_col: str) -> Dict[str, Any]:
        """
        Calculates the distribution of the target variable.
        """
        if target_col not in df.columns:
            self.logger.warning("target_column_not_found", target=target_col)
            return {"error": f"Target column '{target_col}' not found"}
            
        counts = df[target_col].value_counts().to_dict()
        pcts = df[target_col].value_counts(normalize=True).to_dict()
        
        return {
            str(k): {"count": int(v), "percentage": float(round(pcts[k] * 100, 2))}
            for k, v in counts.items()
        }

    def get_shape(self, df: pd.DataFrame) -> Tuple[int, int]:
        """Returns the shape of the DataFrame as (rows, cols)."""
        return df.shape

    def get_memory_usage(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculates memory usage of the DataFrame.
        """
        mem_bytes = df.memory_usage(deep=True).sum()
        return {
            "bytes": int(mem_bytes),
            "megabytes": float(round(mem_bytes / (1024 * 1024), 2))
        }

    def generate_profile_report(self, df: pd.DataFrame, target_col: str = None) -> Dict[str, Any]:
        """
        Generates a comprehensive profile report combining all inspections.
        """
        self.logger.info("generating_profile_report")
        report = {
            "shape": {"rows": df.shape[0], "columns": df.shape[1]},
            "memory": self.get_memory_usage(df),
            "dtypes": self.get_dtypes(df),
            "missing_values": self.get_missing_summary(df),
        }
        
        if target_col and target_col in df.columns:
            report["target_distribution"] = self.get_class_distribution(df, target_col)
            
        return report
