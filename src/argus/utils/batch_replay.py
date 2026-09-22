import pandas as pd
import pyarrow.parquet as pq

class BatchReplay:
    """
    Batch replay utility.
    Reads a parquet file in order in batches.
    Note: This is a batch replay utility, NOT a real-time streaming system.
    """
    
    def __init__(self, file_path: str, batch_size: int = 100):
        self.file_path = file_path
        self.batch_size = batch_size
        self.parquet_file = pq.ParquetFile(file_path)
        
    def iter_batches(self):
        """
        Yields batches of rows as pandas DataFrames in order.
        """
        for batch in self.parquet_file.iter_batches(batch_size=self.batch_size):
            yield batch.to_pandas()
