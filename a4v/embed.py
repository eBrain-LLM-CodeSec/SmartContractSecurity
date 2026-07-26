"""Semantic embeddings for source (F_S) and Commentator comments (F_C).

OpenRouter has no embeddings endpoint, so the primary path is Voyage
`voyage-code-3`. Absent a Voyage key, falls back to a local
sentence-transformers model -- Cisco's SecureBERT 2.0 bi-encoder
(`cisco-ai/SecureBERT2.0-biencoder`, Apache-2.0, natively sentence-
transformers-compatible, 768-dim, cybersecurity-domain-tuned) -- and
warns once at startup. This is a detected, logged degradation of the
*embedding* modality only, not a substitute for a missing program graph
(that stays a hard failure; see graph.py/repair.py). Never fails mid-run
for lack of a Voyage key.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

_LOCAL_FALLBACK_MODEL = "cisco-ai/SecureBERT2.0-biencoder"


class Vectorizer:
    def __init__(self, cache_dir: Path, voyage_key_file: Path | None = None,
                 voyage_model: str = "voyage-code-3", local_fallback_model: str = _LOCAL_FALLBACK_MODEL):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._voyage_client = None
        self._local_model = None
        self.provider: str

        if voyage_key_file and Path(voyage_key_file).exists():
            import voyageai
            api_key = Path(voyage_key_file).read_text().strip()
            self._voyage_client = voyageai.Client(api_key=api_key)
            self._voyage_model = voyage_model
            self.provider = "voyage"
        else:
            print(
                f"WARNING: no Voyage key at {voyage_key_file} -- falling back to local "
                f"sentence-transformers model ({local_fallback_model}). Embedding quality/semantic-recall "
                "will be weaker than voyage-code-3; this does not block the pipeline.",
                file=sys.stderr,
            )
            from sentence_transformers import SentenceTransformer
            self._local_model = SentenceTransformer(local_fallback_model)
            self.provider = "local"
            self._local_fallback_model_name = local_fallback_model

    def _cache_key(self, text: str) -> str:
        tag = self._voyage_model if self.provider == "voyage" else self._local_fallback_model_name
        return hashlib.sha256(f"{self.provider}:{tag}:{text}".encode()).hexdigest()

    def _cache_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def _embed_one(self, text: str, input_type: str) -> np.ndarray:
        key = self._cache_key(text)
        cache_path = self._cache_path(key)
        if cache_path.exists():
            return np.array(json.loads(cache_path.read_text()))

        if self.provider == "voyage":
            resp = self._voyage_client.embed([text], model=self._voyage_model, input_type=input_type)
            vec = np.array(resp.embeddings[0])
        else:
            vec = np.array(self._local_model.encode(text, normalize_embeddings=True))

        cache_path.write_text(json.dumps(vec.tolist()))
        return vec

    def embed_source(self, source: str) -> np.ndarray:
        return self._embed_one(source, input_type="document")

    def embed_comment(self, comment: str) -> np.ndarray:
        return self._embed_one(comment, input_type="query")

    @staticmethod
    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        denom = (np.linalg.norm(a) * np.linalg.norm(b))
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)

    @classmethod
    def from_config(cls, cfg: dict, cache_dir: Path) -> "Vectorizer":
        return cls(
            cache_dir=cache_dir,
            voyage_key_file=cfg.get("voyage_key_file"),
            voyage_model=cfg.get("voyage_model", "voyage-code-3"),
            local_fallback_model=cfg.get("local_fallback_model", _LOCAL_FALLBACK_MODEL),
        )
