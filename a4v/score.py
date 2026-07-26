"""SuspicionRanker: the transparent, untrained fusion of structural,
Commentator, and semantic-similarity signals into a candidate ordering (see
plan: "Multimodal fusion & ranking (the classifier-gap answer)"). This is a
ranker feeding the Auditor, not a decision surface -- the final detect/no-
detect call belongs to the Auditor (Phase 3).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from a4v.commentator import Comment
from a4v.features import NodeFeatures

_SEVERITY_WEIGHT = {"high": 1.0, "medium": 0.6, "low": 0.3, None: 0.0}

# Weights over: cyclomatic_complexity, external_call_count, unsafe_cast_count,
# write_after_external_call_count (in FEATURE_NAMES order), commentator, embedding.
DEFAULT_WEIGHTS = {
    "cyclomatic_complexity": 0.1,
    "external_call_count": 0.15,
    "unsafe_cast_count": 0.25,
    "write_after_external_call_count": 0.35,
    "commentator": 0.6,
    "embedding_similarity": 0.2,
}


@dataclass
class Candidate:
    node_id: str
    score: float
    strong_signal: bool
    features: NodeFeatures
    comment: Comment | None = None
    embedding_similarity: float | None = None
    kept: bool = False  # set by dynamic_threshold


def is_strong_signal(features: NodeFeatures, comment: Comment | None) -> bool:
    """Strong-signal candidates are never dropped by the dynamic threshold
    (plan: "Always preserve candidates with a strong static-analysis or
    Commentator signal, regardless of threshold")."""
    if features.write_after_external_call_count > 0:
        return True
    if features.unsafe_cast_count > 0:
        return True
    if comment is not None and comment.suspicious and comment.severity in ("medium", "high"):
        return True
    return False


class SuspicionRanker:
    def __init__(self, weights: dict[str, float] | None = None):
        self.weights = weights or DEFAULT_WEIGHTS

    def _combine(self, z_features: dict[str, float], comment: Comment | None,
                 embedding_similarity: float | None) -> float:
        score = 0.0
        for name, weight in self.weights.items():
            if name == "commentator":
                if comment is not None and comment.suspicious:
                    score += weight * _SEVERITY_WEIGHT.get(comment.severity, 0.5)
                continue
            if name == "embedding_similarity":
                if embedding_similarity is not None:
                    score += weight * max(embedding_similarity, 0.0)
                continue
            score += weight * z_features.get(name, 0.0)
        return score

    def rank(self, raw_features: dict[str, NodeFeatures], z_features: dict[str, dict[str, float]],
              comments: dict[str, Comment] | None = None,
              embedding_similarities: dict[str, float] | None = None) -> list[Candidate]:
        comments = comments or {}
        embedding_similarities = embedding_similarities or {}
        candidates = []
        for node_id, features in raw_features.items():
            comment = comments.get(node_id)
            sim = embedding_similarities.get(node_id)
            score = self._combine(z_features.get(node_id, {}), comment, sim)
            candidates.append(Candidate(
                node_id=node_id, score=score,
                strong_signal=is_strong_signal(features, comment),
                features=features, comment=comment, embedding_similarity=sim,
            ))
        candidates.sort(key=lambda c: c.score, reverse=True)
        return candidates


def dynamic_threshold(candidates: list[Candidate], mode: str = "percentile",
                       percentile: float = 0.7, gap_ratio: float = 2.0) -> list[Candidate]:
    """Marks `.kept = True` on candidates that clear a dynamic threshold OR
    carry a strong signal (never dropped). No fixed K (plan: "Dynamic
    candidate selection (removes the fixed-K bottleneck)").

    mode="percentile": keep candidates scoring at/above the given percentile
    of the score distribution.
    mode="gap": keep the top run of candidates before the first big
    relative drop (score[i] / score[i+1] >= gap_ratio), i.e. before the
    "cliff" in a sorted-descending score list.
    """
    if not candidates:
        return candidates

    scores = np.array([c.score for c in candidates])

    if mode == "percentile":
        cutoff = float(np.percentile(scores, percentile * 100))
    elif mode == "gap":
        cutoff = scores.min() - 1.0  # keep everyone unless a gap is found
        for i in range(len(scores) - 1):
            hi, lo = scores[i], scores[i + 1]
            if hi <= 0:
                continue
            if lo <= 0 or hi / max(lo, 1e-9) >= gap_ratio:
                cutoff = lo
                break
    else:
        raise ValueError(f"unknown threshold mode {mode!r}")

    for c in candidates:
        c.kept = c.strong_signal or c.score >= cutoff
    return candidates
