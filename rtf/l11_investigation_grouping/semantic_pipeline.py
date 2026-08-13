"""RTF v2: orchestration + observability for the semantic-property stage.

Ties `semantic_property_generation.py` (Phase 5) and `property_grounding.py`
(Phase 6/7) together into one call, and serializes every intermediate
artifact the task brief's Section 19 asks for -- so a miss can be
diagnosed as "context extraction failed" / "generation proposed nothing" /
"proposed but rejected at grounding" / "grounded but not clustered with
the right property" / "clustered but the investigator missed it", never
collapsed into an undifferentiated "RTF missed it" (see
RTF_V2_ARCHITECTURE.md section C.6/Section 19 of the task brief).

Deliberately thin: every real decision already lives in the two modules
above; this module only composes + writes JSON, matching
`context_artifacts.py`'s own "separate generation from I/O" convention.
"""
from __future__ import annotations

import json
from pathlib import Path

from rtf.l11_investigation_grouping.property_grounding import (
    RejectedProperty, ground_semantic_properties, merge_property_pools, rejected_property_to_dict,
)
from rtf.l11_investigation_grouping.property_metadata import PropertyMetadata
from rtf.l11_investigation_grouping.semantic_property_generation import (
    GenerationRejection, ProjectManifest, generate_semantic_properties, raw_property_to_dict,
)


def generate_and_ground_semantic_properties(
    protocol_context_md: str, manifest: ProjectManifest, chat_client, slither=None,
    max_properties: int = 12, temperature: float = 0.0,
) -> tuple[list[PropertyMetadata], dict]:
    """Runs Phase 5 then Phase 6. Returns (grounded_properties,
    observability) where `observability` has keys `"raw"` (every
    proposed `RawSemanticProperty`, as dicts), `"rejected_generation"`
    (basic-shape/discipline failures), `"rejected_grounding"` (shape-valid
    but ungrounded properties) -- every one of Section 19's three
    semantic-stage failure points is independently inspectable here, not
    collapsed into a single pass/fail count."""
    raw, rejected_generation = generate_semantic_properties(
        protocol_context_md, manifest, chat_client, max_properties=max_properties, temperature=temperature,
    )
    grounded, rejected_grounding = ground_semantic_properties(raw, manifest, slither=slither)
    observability = {
        "raw": [raw_property_to_dict(r) for r in raw],
        "rejected_generation": [_generation_rejection_to_dict(r) for r in rejected_generation],
        "rejected_grounding": [rejected_property_to_dict(r) for r in rejected_grounding],
    }
    return grounded, observability


def _generation_rejection_to_dict(rejection: GenerationRejection) -> dict:
    from rtf.l11_investigation_grouping.semantic_property_generation import rejection_to_dict
    return rejection_to_dict(rejection)


def build_full_property_pool(
    structural_properties: list[PropertyMetadata], protocol_context_md: str, manifest: ProjectManifest,
    chat_client, slither=None, max_properties: int = 12,
) -> tuple[list[PropertyMetadata], dict]:
    """Phase 7: the full RTF v2 property pool for one audit -- structural/
    requirement-derived properties (unchanged, from
    `live_runner.build_property_pool`) merged with the newly generated and
    grounded semantic pool (deduplicated). Returns (merged_pool,
    observability) -- `observability` extends `generate_and_ground_
    semantic_properties`'s own dict with `"structural_count"` and
    `"semantic_grounded_count"` (post-dedup) so the merge itself is
    auditable, not just its two inputs."""
    grounded, observability = generate_and_ground_semantic_properties(
        protocol_context_md, manifest, chat_client, slither=slither, max_properties=max_properties,
    )
    merged = merge_property_pools(structural_properties, grounded)
    semantic_in_pool = [p for p in merged if p.source_kind == "code_semantics"]
    observability["structural_count"] = len(structural_properties)
    observability["semantic_grounded_count"] = len(semantic_in_pool)
    return merged, observability


def _property_to_observability_dict(p: PropertyMetadata) -> dict:
    return {
        "property_id": p.property_id, "requirement_id": p.requirement_id,
        "requirement_level": p.requirement_level, "source_kind": p.source_kind,
        "generation_method": p.generation_method, "property_text": p.property_text,
        "target_contract": p.target_contract, "target_function": p.target_function,
        "reasoning_category": p.reasoning_category.value if p.reasoning_category else None,
        "confidence": p.confidence, "rationale": p.rationale,
        "grounding_evidence": list(p.grounding_evidence),
        "relevant_state_variables": list(p.relevant_state_variables),
    }


def write_observability_artifacts(
    root: Path, audit_id: str, *,
    applicable_standards: list[dict] | None = None,
    structural_properties: list[PropertyMetadata] | None = None,
    semantic_pipeline_observability: dict | None = None,
    semantic_properties_grounded: list[PropertyMetadata] | None = None,
    property_clusters: list[dict] | None = None,
) -> dict[str, str]:
    """Writes the Section-19 observability artifacts under
    `root/.rtf/observability/` (a sibling of `context_artifacts.py`'s own
    `.rtf/context`/`.rtf/plans`, same convention). Every argument is
    optional and independently written -- a caller that only ran part of
    the pipeline (e.g. context extraction failed before generation ever
    ran) still gets whatever DID run persisted, rather than an all-or-
    nothing dump. Returns {logical_name: relative_path_written}."""
    out_dir = root / ".rtf" / "observability"
    out_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}

    def _write(name: str, payload) -> None:
        path = out_dir / name
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        written[name.rsplit(".", 1)[0]] = str(path.relative_to(root))

    if applicable_standards is not None:
        _write("applicable_standards.json", applicable_standards)
    if structural_properties is not None:
        _write("structural_properties.json", [_property_to_observability_dict(p) for p in structural_properties])
    if semantic_pipeline_observability is not None:
        _write("semantic_properties_raw.json", semantic_pipeline_observability.get("raw", []))
        _write("rejected_properties.json", {
            "rejected_generation": semantic_pipeline_observability.get("rejected_generation", []),
            "rejected_grounding": semantic_pipeline_observability.get("rejected_grounding", []),
        })
    if semantic_properties_grounded is not None:
        _write("semantic_properties_grounded.json", [_property_to_observability_dict(p) for p in semantic_properties_grounded])
    if property_clusters is not None:
        _write("property_clusters.json", property_clusters)

    return written
