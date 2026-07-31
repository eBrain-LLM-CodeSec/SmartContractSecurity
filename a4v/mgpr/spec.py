"""Loads and validates routing_spec.yaml into typed Gate/FamilySpec objects.

See /scratch/md5344/.claude/plans/effervescent-inventing-teapot.md section 3
for the P1/P2/P5 v1 slice this loader targets. Families with
`status: NOT_YET_SPECIFIED` are loaded as bare stubs (no gates/context) and
are simply skipped by the router -- they are not an error, just not
implemented yet, and this loader must not silently invent gates for them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

_VALID_STATUSES = {"SPECIFIED", "NOT_YET_SPECIFIED"}
_VALID_SEED_TYPES = {"function", "contract", "shared_state_cluster"}


class SpecError(ValueError):
    """Raised on any malformed or unresolvable routing_spec.yaml content."""


@dataclass(frozen=True)
class Gate:
    id: str
    # {"all": [str, ...]} where each item is either a bare predicate name
    # (boolean predicate) or {"equals": {name: value}} (enum predicate) --
    # see a4v/mgpr/router.py for how this is evaluated.
    predicate: dict


@dataclass(frozen=True)
class ContextPolicy:
    include: list[str] = field(default_factory=list)
    stop: list[str] = field(default_factory=list)
    deferred: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FamilySpec:
    name: str
    status: str  # SPECIFIED | NOT_YET_SPECIFIED
    seed_types: list[str] = field(default_factory=list)
    gates: list[Gate] = field(default_factory=list)
    context_policy: ContextPolicy | None = None
    prompt_id: str | None = None
    params: dict = field(default_factory=dict)


@dataclass(frozen=True)
class RoutingSpec:
    version: int
    families: dict[str, FamilySpec]

    def specified_families(self) -> list[FamilySpec]:
        return [f for f in self.families.values() if f.status == "SPECIFIED"]


def _parse_predicate_item(item, family_name: str, gate_id: str):
    if isinstance(item, str):
        return item
    if isinstance(item, dict) and set(item.keys()) == {"equals"}:
        eq = item["equals"]
        if not (isinstance(eq, dict) and len(eq) == 1):
            raise SpecError(f"{family_name}/{gate_id}: malformed 'equals' predicate: {item!r}")
        return {"equals": eq}
    raise SpecError(f"{family_name}/{gate_id}: unrecognized predicate item {item!r}")


def _parse_predicate(raw, family_name: str, gate_id: str) -> dict:
    if not isinstance(raw, dict) or set(raw.keys()) != {"all"}:
        raise SpecError(f"{family_name}/{gate_id}: predicate must be a dict with only an 'all' key, got {raw!r}")
    items = raw["all"]
    if not isinstance(items, list) or not items:
        raise SpecError(f"{family_name}/{gate_id}: predicate.all must be a non-empty list")
    return {"all": [_parse_predicate_item(item, family_name, gate_id) for item in items]}


def _parse_family(name: str, fdata: dict) -> FamilySpec:
    if not isinstance(fdata, dict) or "status" not in fdata:
        raise SpecError(f"{name}: missing 'status'")
    status = fdata["status"]
    if status not in _VALID_STATUSES:
        raise SpecError(f"{name}: invalid status {status!r}, must be one of {sorted(_VALID_STATUSES)}")

    if status == "NOT_YET_SPECIFIED":
        extra_keys = set(fdata.keys()) - {"status"}
        if extra_keys:
            raise SpecError(
                f"{name}: status is NOT_YET_SPECIFIED but has extra keys {sorted(extra_keys)} -- "
                "a stub family must carry no gate/context content"
            )
        return FamilySpec(name=name, status=status)

    seed_types = fdata.get("seed_types", [])
    if not seed_types:
        raise SpecError(f"{name}: SPECIFIED family requires a non-empty seed_types list")
    for st in seed_types:
        if st not in _VALID_SEED_TYPES:
            raise SpecError(f"{name}: unknown seed_type {st!r}, must be one of {sorted(_VALID_SEED_TYPES)}")

    gates_raw = fdata.get("gates") or []
    if not gates_raw:
        raise SpecError(f"{name}: SPECIFIED family requires at least one gate")
    gates = []
    for g in gates_raw:
        if "id" not in g or "predicate" not in g:
            raise SpecError(f"{name}: gate missing 'id' or 'predicate': {g!r}")
        gates.append(Gate(id=g["id"], predicate=_parse_predicate(g["predicate"], name, g["id"])))

    cp_raw = fdata.get("context_policy") or {}
    context_policy = ContextPolicy(
        include=list(cp_raw.get("include", [])),
        stop=list(cp_raw.get("stop", [])),
        deferred=list(cp_raw.get("deferred", [])),
    )

    prompt_id = fdata.get("prompt_id")
    if not prompt_id:
        raise SpecError(f"{name}: SPECIFIED family requires a prompt_id")

    return FamilySpec(
        name=name,
        status=status,
        seed_types=seed_types,
        gates=gates,
        context_policy=context_policy,
        prompt_id=prompt_id,
        params=dict(fdata.get("params", {})),
    )


def load_routing_spec(path: str | Path, known_predicates: set[str] | None = None) -> RoutingSpec:
    """Load and validate routing_spec.yaml. If `known_predicates` is given,
    every predicate name referenced by a SPECIFIED family's gates must be a
    member of it, or loading fails -- this catches a typo'd or
    not-yet-implemented predicate name at load time rather than at route
    time.
    """
    raw = yaml.safe_load(Path(path).read_text())
    if not isinstance(raw, dict) or "families" not in raw:
        raise SpecError(f"{path}: missing top-level 'families' key")

    families = {name: _parse_family(name, fdata) for name, fdata in raw["families"].items()}
    spec = RoutingSpec(version=int(raw.get("version", 1)), families=families)

    if known_predicates is not None:
        for family in spec.specified_families():
            for gate in family.gates:
                for item in gate.predicate["all"]:
                    pred_name = item if isinstance(item, str) else next(iter(item["equals"]))
                    if pred_name not in known_predicates:
                        raise SpecError(
                            f"{family.name}/{gate.id}: predicate {pred_name!r} is not in the known "
                            f"predicate registry {sorted(known_predicates)}"
                        )
    return spec
