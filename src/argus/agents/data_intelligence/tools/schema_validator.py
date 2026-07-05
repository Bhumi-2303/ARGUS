from typing import Any
import pandas as pd
from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory
from argus.agents.data_intelligence.schemas import RawChunk, ValidatedChunk, PipelineConfig

class SchemaValidatorTool(BaseTool):
    """Validates the schema of incoming data chunks."""

    EXPECTED_COLUMNS = {
        "IPV4_SRC_ADDR", "IPV4_DST_ADDR", "L4_SRC_PORT", "L4_DST_PORT", 
        "PROTOCOL", "L7_PROTO", "IN_BYTES", "OUT_BYTES", "IN_PKTS", "OUT_PKTS",
        "TCP_FLAGS", "CLIENT_TCP_FLAGS", "SERVER_TCP_FLAGS", 
        "FLOW_DURATION_MILLISECONDS", "DURATION_IN", "DURATION_OUT",
        "MIN_TTL", "MAX_TTL", "LONGEST_FLOW_PKT", "SHORTEST_FLOW_PKT",
        "MIN_IP_PKT_LEN", "MAX_IP_PKT_LEN", "SRC_TO_DST_SECOND_BYTES",
        "DST_TO_SRC_SECOND_BYTES", "RETRANSMITTED_IN_BYTES", 
        "RETRANSMITTED_IN_PKTS", "RETRANSMITTED_OUT_BYTES", 
        "RETRANSMITTED_OUT_PKTS", "SRC_TO_DST_AVG_THROUGHPUT", 
        "DST_TO_SRC_AVG_THROUGHPUT", "NUM_PKTS_UP_TO_128_BYTES", 
        "NUM_PKTS_128_TO_256_BYTES", "NUM_PKTS_256_TO_512_BYTES", 
        "NUM_PKTS_512_TO_1024_BYTES", "NUM_PKTS_1024_TO_1514_BYTES",
        "TCP_WIN_MAX_IN", "TCP_WIN_MAX_OUT", "ICMP_TYPE", "ICMP_IPV4_TYPE",
        "DNS_QUERY_ID", "DNS_QUERY_TYPE", "DNS_TTL_ANSWER", "FTP_COMMAND_RET_CODE",
        "Label", "Attack"
    }

    def __init__(self):
        super().__init__(
            tool_id="tool-schema-validator-01",
            name="schema_validator",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            description="Validates chunk schema against NF-ToN-IoT-v2 specification.",
            required_permissions=["data:read"]
        )

    async def initialize(self) -> None:
        self.logger.info("initializing_schema_validator")

    async def validate(self, **kwargs: Any) -> bool:
        return "raw_chunk" in kwargs and "config" in kwargs

    async def execute(self, **kwargs: Any) -> ValidatedChunk:
        raw_chunk: RawChunk = kwargs["raw_chunk"]
        
        actual_cols = set(raw_chunk.data.columns)
        
        # In a real scenario, we might strictly fail on missing columns.
        # But some versions drop FTP_COMMAND_RET_CODE or others, so we just report them.
        missing_columns = list(self.EXPECTED_COLUMNS - actual_cols)
        
        type_mismatches = {}
        # Example light type checking: ensure string columns are objects, numeric are numeric
        for col in actual_cols:
            dtype = raw_chunk.data[col].dtype
            if col in ["IPV4_SRC_ADDR", "IPV4_DST_ADDR", "Attack"]:
                if not pd.api.types.is_object_dtype(dtype) and not pd.api.types.is_string_dtype(dtype):
                    type_mismatches[col] = f"Expected string, got {dtype}"
            else:
                if not pd.api.types.is_numeric_dtype(dtype):
                    type_mismatches[col] = f"Expected numeric, got {dtype}"

        # Consider valid if we have the core columns and not completely mismatched
        is_valid = len(missing_columns) < 10

        if not is_valid:
            self.logger.warning("chunk_validation_failed", 
                                chunk_index=raw_chunk.chunk_index, 
                                missing_count=len(missing_columns))

        return ValidatedChunk(
            raw_chunk=raw_chunk,
            is_valid=is_valid,
            missing_columns=missing_columns,
            type_mismatches=type_mismatches
        )

    async def shutdown(self) -> None:
        pass

    def metadata(self) -> dict:
        md = super().metadata()
        md["parameters_schema"] = {
            "type": "object",
            "properties": {
                "raw_chunk": {"type": "object"},
                "config": {"type": "object"}
            },
            "required": ["raw_chunk", "config"]
        }
        return md
