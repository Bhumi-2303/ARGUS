import os
import pandas as pd
from typing import Iterator, List, Optional
from pathlib import Path

from training.utils.config_manager import ConfigurationManager
from training.utils.logger import get_logger

class CSVLoader:
    """Loads CSV datasets, supporting chunked loading for memory efficiency."""
    
    def __init__(self, config: ConfigurationManager):
        """
        Initializes the CSVLoader.
        
        Args:
            config: ConfigurationManager instance containing dataset config.
        """
        self.config = config
        self.logger = get_logger(__name__)
        
    def load(self, file_path: str) -> pd.DataFrame:
        """
        Loads an entire CSV file into memory.
        
        Args:
            file_path: Path to the CSV file.
            
        Returns:
            pd.DataFrame: The loaded dataset.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file is not a valid CSV or has encoding issues.
        """
        path = Path(file_path)
        if not path.exists():
            self.logger.error("file_not_found", path=str(path))
            raise FileNotFoundError(f"Dataset file not found: {path}")
            
        try:
            self.logger.info("loading_csv", path=str(path))
            df = pd.read_csv(path)
            self.logger.info("csv_loaded", shape=df.shape, path=str(path))
            return df
        except Exception as e:
            self.logger.error("csv_load_failed", error=str(e), path=str(path))
            raise ValueError(f"Failed to load CSV {path}: {e}")

    def load_chunked(self, file_path: str, chunk_size: Optional[int] = None) -> Iterator[pd.DataFrame]:
        """
        Yields chunks of the CSV file for memory-efficient processing.
        
        Args:
            file_path: Path to the CSV file.
            chunk_size: Number of rows per chunk. Defaults to config value.
            
        Yields:
            pd.DataFrame: A chunk of the dataset.
        """
        path = Path(file_path)
        if not path.exists():
            self.logger.error("file_not_found", path=str(path))
            raise FileNotFoundError(f"Dataset file not found: {path}")
            
        chunk_size = chunk_size or self.config.get("hardware.chunk_size", 50000)
        
        try:
            self.logger.info("loading_csv_chunked", path=str(path), chunk_size=chunk_size)
            for chunk_idx, chunk in enumerate(pd.read_csv(path, chunksize=chunk_size)):
                self.logger.debug("yielded_chunk", chunk_index=chunk_idx, shape=chunk.shape)
                yield chunk
        except Exception as e:
            self.logger.error("csv_chunk_load_failed", error=str(e), path=str(path))
            raise ValueError(f"Failed to load CSV chunks from {path}: {e}")

    def validate_schema(self, df: pd.DataFrame, expected_columns: List[str]) -> bool:
        """
        Validates that the DataFrame contains the expected columns.
        
        Args:
            df: The DataFrame to validate.
            expected_columns: List of column names that must exist.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        missing_cols = [col for col in expected_columns if col not in df.columns]
        if missing_cols:
            self.logger.warning("schema_validation_failed", missing_columns=missing_cols)
            return False
        return True

    def get_file_info(self, file_path: str) -> dict:
        """
        Returns basic file metadata without loading the CSV into pandas.
        
        Args:
            file_path: Path to the CSV file.
            
        Returns:
            dict: Metadata including size in bytes.
        """
        path = Path(file_path)
        if not path.exists():
            return {"error": "File not found"}
        
        stat = os.stat(path)
        return {
            "path": str(path),
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2)
        }

    def __repr__(self) -> str:
        return f"CSVLoader(config={self.config})"
