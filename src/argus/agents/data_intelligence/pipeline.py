import time
from typing import AsyncIterator
from argus.schemas.messages import FeatureEvent
from argus.agents.data_intelligence.schemas import PipelineConfig
from argus.agents.data_intelligence.tools import (
    DataLoaderTool,
    SchemaValidatorTool,
    DataCleanerTool,
    NormalizerTool,
    FeatureExtractorTool,
    PublisherTool
)

class DataPipeline:
    """Orchestrates the 6-stage data processing pipeline."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        
        # Instantiate pipeline tools
        self.loader = DataLoaderTool()
        self.validator = SchemaValidatorTool()
        self.cleaner = DataCleanerTool()
        self.normalizer = NormalizerTool()
        self.extractor = FeatureExtractorTool()
        self.publisher = PublisherTool()

    async def initialize(self) -> None:
        """Initialize all pipeline tools."""
        await self.loader.initialize()
        await self.validator.initialize()
        await self.cleaner.initialize()
        await self.normalizer.initialize()
        await self.extractor.initialize()
        await self.publisher.initialize()

    async def shutdown(self) -> None:
        """Shutdown all pipeline tools."""
        await self.loader.shutdown()
        await self.validator.shutdown()
        await self.cleaner.shutdown()
        await self.normalizer.shutdown()
        await self.extractor.shutdown()
        await self.publisher.shutdown()

    async def process_file(self, file_path: str, config: PipelineConfig) -> AsyncIterator[FeatureEvent]:
        """Stream-process a CSV/Parquet file in chunks, yielding a FeatureEvent per chunk."""
        
        chunk_count = 0
        async for raw_chunk in self.loader.execute(file_path=file_path, chunk_size=config.chunk_size):
            start_time = time.time()
            
            validated = await self.validator.execute(raw_chunk=raw_chunk, config=config)
            cleaned = await self.cleaner.execute(validated_chunk=validated, config=config)
            normalized = await self.normalizer.execute(cleaned_chunk=cleaned, config=config)
            features = await self.extractor.execute(normalized_chunk=normalized)
            
            event = await self.publisher.execute(
                extracted_features=features,
                agent_id=self.agent_id,
                start_time=start_time
            )
            
            yield event
            
            chunk_count += 1
            if config.max_chunks is not None and chunk_count >= config.max_chunks:
                break

