from typing import List
from pydantic import BaseModel, Field
from collections import namedtuple


class Parameters(BaseModel):
    clusters_index: str
    answers_index: str
    stopwords_files: List[str]
    max_hits: int
    chunk_size: int
    sbert_score: float
    candidates_quantity: int
    host: str
    port: int


UserQuery = namedtuple("UserQuery", "new_licensesId, BitrixId, serverTimestamp, payload_request_string")
