from typing import Optional
from uuid import UUID

from src.storage.repositories import FundChunkRepository
from src.storage.tables import FundChunkTable


class ChunkService:
    def __init__(self, chunk_repo: FundChunkRepository):
        self._chunk_repo = chunk_repo

    def find_similar(
        self,
        embedding: list[float],
        limit: int = 8,
        fund_id: Optional[UUID] = None,
    ) -> list[FundChunkTable]:
        return self._chunk_repo.find_similar(embedding, limit=limit, fund_id=fund_id)
