"""Vectorizer local-fallback embedding path (Cisco's SecureBERT 2.0
bi-encoder, cisco-ai/SecureBERT2.0-biencoder).

Downloads real model weights (~570MB) from HuggingFace on first run --
gated behind RUN_MODEL_DOWNLOAD_TESTS=1 so a plain `pytest` run stays fast
and offline by default, same pattern as the RUN_LLM_TESTS-gated tests in
tests/integration/.
"""
import os
from pathlib import Path

import pytest

from a4v.embed import _LOCAL_FALLBACK_MODEL, Vectorizer

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_MODEL_DOWNLOAD_TESTS") != "1",
    reason="downloads real model weights (~570MB) from HuggingFace; set RUN_MODEL_DOWNLOAD_TESTS=1 to run",
)


def test_local_fallback_model_is_securebert():
    assert _LOCAL_FALLBACK_MODEL == "cisco-ai/SecureBERT2.0-biencoder"


def test_local_fallback_produces_768_dim_embeddings(tmp_path):
    v = Vectorizer(cache_dir=tmp_path / "cache", voyage_key_file=Path("/nonexistent/voyage.key"))
    assert v.provider == "local"

    e1 = v.embed_source(
        "function withdraw(uint256 amount) external { "
        "(bool ok,) = msg.sender.call{value: amount}(''); balances[msg.sender] -= amount; }"
    )
    e2 = v.embed_source("function deposit() external payable { balances[msg.sender] += msg.value; }")

    assert e1.shape == (768,)
    assert e2.shape == (768,)


def test_local_fallback_self_similarity_is_one(tmp_path):
    v = Vectorizer(cache_dir=tmp_path / "cache", voyage_key_file=Path("/nonexistent/voyage.key"))
    e1 = v.embed_source("function withdraw(uint256 amount) external {}")
    assert v.cosine_similarity(e1, e1) == pytest.approx(1.0, abs=1e-4)


def test_local_fallback_distinguishes_dissimilar_functions(tmp_path):
    v = Vectorizer(cache_dir=tmp_path / "cache", voyage_key_file=Path("/nonexistent/voyage.key"))
    withdraw = v.embed_source(
        "function withdraw(uint256 amount) external { "
        "(bool ok,) = msg.sender.call{value: amount}(''); balances[msg.sender] -= amount; }"
    )
    unrelated = v.embed_source("function getName() external pure returns (string memory) { return 'Token'; }")
    sim = v.cosine_similarity(withdraw, unrelated)
    assert 0.0 <= sim < 0.99, f"expected non-degenerate similarity, got {sim}"
