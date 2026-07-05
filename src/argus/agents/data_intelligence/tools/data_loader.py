import asyncio
import os
import pandas as pd
from typing import Any, AsyncIterator
import pyarrow.parquet as pq

from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory
from argus.agents.data_intelligence.schemas import RawChunk

class DataLoaderTool(BaseTool):
    """Loads CSV or Parquet files in chunks."""

    def __init__(self):
        super().__init__(
            tool_id="tool-data-loader-01",
            name="data_loader",
            version="1.0.0",
            category=ToolCategory.FILESYSTEM,
            description="Loads large CSV or Parquet datasets in chunks.",
            required_permissions=["data:read"]
        )

    async def initialize(self) -> None:
        self.logger.info("initializing_data_loader")

    async def validate(self, **kwargs: Any) -> bool:
        file_path = kwargs.get("file_path")
        if not file_path or not os.path.exists(file_path):
            self.logger.error("invalid_file_path", file_path=file_path)
            return False
        return True

    async def execute(self, **kwargs: Any) -> AsyncIterator[RawChunk]:
        """Executes the data load and yields RawChunks."""
        file_path = kwargs["file_path"]
        chunk_size = kwargs.get("chunk_size", 10000)

        if file_path.endswith('.parquet'):
            pf = await asyncio.to_thread(pq.ParquetFile, file_path)
            iterator = pf.iter_batches(batch_size=chunk_size)
            i = 0
            while True:
                try:
                    batch = await asyncio.to_thread(next, iterator)
                    df = batch.to_pandas()
                    yield RawChunk(
                        file_path=file_path,
                        chunk_index=i,
                        data=df,
                        row_count=len(df)
                    )
                    i += 1
                except StopIteration:
                    break
                except Exception as e:
                    self.logger.error("parquet_read_error", error=str(e), exc_info=True)
                    raise e
        else:
            # We wrap the pandas read_csv chunked iterator
            iterator = pd.read_csv(file_path, chunksize=chunk_size)
            i = 0
            while True:
                try:
                    chunk = await asyncio.to_thread(next, iterator)
                    yield RawChunk(
                        file_path=file_path,
                        chunk_index=i,
                        data=chunk,
                        row_count=len(chunk)
                    )
                    i += 1
                except StopIteration:
                    break
                except Exception as e:
                    self.logger.error("csv_read_error", error=str(e), exc_info=True)
                    raise e


    async def shutdown(self) -> None:
        self.logger.info("shutting_down_data_loader")

    def metadata(self) -> dict:
        md = super().metadata()
        md["parameters_schema"] = {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "chunk_size": {"type": "integer"}
            },
            "required": ["file_path"]
        }
        return md
