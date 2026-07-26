"""A2 -- label parsing (see plan A2).

Parses raw per-contract vulnerability annotations into a `LabelRecord`,
explicit about file/line references and source granularity. Line numbers are
always normalized to **1-indexed, inclusive**, to match `graph.py`'s
`_lines()` (which reads Slither's `source_mapping.lines`, itself 1-indexed) --
callers pass `line_base=0` if the raw dataset's line numbers start at 0.

**`parse_labels`/`_parse_one_annotation` below are the *provisional*,
now-superseded-by-real-data parser**: the field-name aliases
(`_LINE_START_FIELDS` etc.) mirror `discover.py`'s original format-agnostic
heuristics, written before A0's download. Kept as a generic fallback for
JSON/CSV-shaped label sources, but **the real Resource 2 format is
completely different** (see `parse_messiq_name_label_pairs` below) --
per-vuln-class parallel `final_<class>_name.txt` (bare filenames, one per
line) / `final_<class>_label.txt` (bare `0`/`1`, positionally paired, same
line count). Not JSON, not CSV, no file/line/function fields at all --
label granularity here is genuinely **file**, one flag per named `.sol`
sample. Confirmed via manual inspection across all 4 vuln classes; see
`data/gnn/raw/MANIFEST.md` finding 2.

A second confirmed fact (MANIFEST.md finding 3) that shapes the join key
below: **per-class sample ids are not globally unique** --
`reentrancy/3.sol` and `Integeroverflow/3.sol` are different contracts that
happen to share the numeral "3" (confirmed via differing sha256). So
`native_id` here is always `f"{vuln_class}/{name}"`, never the bare
filename -- and this also means Resource 2 is effectively **four
independent single-label corpora**, not one multi-label corpus: the same
underlying contract essentially never appears labeled for more than one
class (A3's cross-class dedup will only fire on incidental sha256
collisions, not by design).
"""
from __future__ import annotations

from dataclasses import dataclass

_NATIVE_ID_FIELDS = ("native_id", "id", "contract_id", "name")
_CLASS_FIELDS = ("vulnerability", "vuln", "vuln_type", "type", "category", "label", "class", "cwe", "bug_type")
_FILE_FIELDS = ("file", "filename", "path", "source", "source_file")
_LINE_FIELDS = ("line", "lines", "loc", "line_no", "lineno")
_LINE_START_FIELDS = ("line_start", "start_line", "begin_line")
_LINE_END_FIELDS = ("line_end", "end_line", "finish_line")
_CONTRACT_FIELDS = ("contract", "contract_name")
_FUNCTION_FIELDS = ("function", "func", "func_name", "function_name", "method")
_SIGNATURE_FIELDS = ("signature", "sig", "function_signature")


class LabelParseError(ValueError):
    pass


@dataclass(frozen=True)
class Annotation:
    vuln_class: str
    file: str | None = None
    lines: tuple[int, ...] = ()  # 1-indexed, inclusive
    contract: str | None = None
    function_name: str | None = None
    signature: str | None = None

    @property
    def granularity(self) -> str:
        if self.lines:
            return "line"
        if self.function_name:
            return "function"
        return "file"


@dataclass(frozen=True)
class LabelRecord:
    native_id: str
    granularity: str  # finest granularity present across this record's annotations
    annotations: tuple[Annotation, ...] = ()


def _first(rec: dict, names: tuple[str, ...]) -> object | None:
    lower = {str(k).lower(): v for k, v in rec.items()}
    for name in names:
        if name in lower and lower[name] not in (None, "", []):
            return lower[name]
    return None


def _normalize_lines(rec: dict, line_base: int) -> tuple[int, ...]:
    shift = 1 - line_base  # line_base=1 -> shift 0; line_base=0 -> shift +1
    raw_lines = _first(rec, _LINE_FIELDS)
    if raw_lines is not None:
        if isinstance(raw_lines, (list, tuple)):
            return tuple(sorted(int(n) + shift for n in raw_lines))
        return (int(raw_lines) + shift,)

    start = _first(rec, _LINE_START_FIELDS)
    end = _first(rec, _LINE_END_FIELDS)
    if start is not None:
        start = int(start) + shift
        end = int(end) + shift if end is not None else start
        if end < start:
            raise LabelParseError(f"line_end {end} < line_start {start} in {rec!r}")
        return tuple(range(start, end + 1))
    return ()


def _parse_one_annotation(rec: dict, line_base: int) -> Annotation:
    vuln_class = _first(rec, _CLASS_FIELDS)
    if vuln_class is None:
        raise LabelParseError(f"no vuln-class field found in {rec!r}")
    if isinstance(vuln_class, list):
        # Multi-class single record isn't handled here -- caller should
        # expand it before calling parse_labels if this shape shows up in
        # the real data; keep this module's contract to one class per
        # Annotation.
        raise LabelParseError(f"expected a single vuln class, got a list: {rec!r}")

    lines = _normalize_lines(rec, line_base)
    file_ = _first(rec, _FILE_FIELDS)
    contract = _first(rec, _CONTRACT_FIELDS)
    function_name = _first(rec, _FUNCTION_FIELDS)
    signature = _first(rec, _SIGNATURE_FIELDS)

    return Annotation(
        vuln_class=str(vuln_class),
        file=str(file_) if file_ is not None else None,
        lines=lines,
        contract=str(contract) if contract is not None else None,
        function_name=str(function_name) if function_name is not None else None,
        signature=str(signature) if signature is not None else None,
    )


_GRANULARITY_RANK = {"line": 2, "function": 1, "file": 0}


def parse_labels(raw: list[dict], *, line_base: int = 1) -> dict[str, LabelRecord]:
    """`raw` is a flat list of annotation dicts, each identifying its owning
    contract via one of `_NATIVE_ID_FIELDS`. Multiple annotations for the
    same native_id are grouped into one `LabelRecord`.
    """
    by_native: dict[str, list[Annotation]] = {}
    for rec in raw:
        native_id = _first(rec, _NATIVE_ID_FIELDS)
        if native_id is None:
            raise LabelParseError(f"no native_id field found in {rec!r}")
        native_id = str(native_id)
        ann = _parse_one_annotation(rec, line_base)
        by_native.setdefault(native_id, []).append(ann)

    records: dict[str, LabelRecord] = {}
    for native_id, anns in by_native.items():
        finest = max(anns, key=lambda a: _GRANULARITY_RANK[a.granularity])
        records[native_id] = LabelRecord(
            native_id=native_id,
            granularity=finest.granularity,
            annotations=tuple(anns),
        )
    return records


def parse_messiq_name_label_pairs(
    name_file: str | Path, label_file: str | Path, vuln_class: str,
) -> dict[str, LabelRecord]:
    """The **real** Resource 2 parser. `name_file` is `final_<class>_name.txt`
    (one bare filename per line, e.g. `"3.sol"`), `label_file` is the
    positionally-paired `final_<class>_label.txt` (one bare `"0"`/`"1"` per
    line). Both must have the same line count.

    `native_id = f"{vuln_class}/{name}"` (see module docstring -- ids collide
    across classes, so the class must be part of the key). A `"1"` line
    produces one graph-level `Annotation(vuln_class=vuln_class)` (no file/
    line/function info -- this format doesn't carry any); a `"0"` line
    produces an **empty** annotations tuple (absence of a positive annotation
    is how "not vulnerable for this class" is represented throughout this
    module -- consistent with `map_labels.py`'s file-granularity handling,
    which zero-initializes and only sets classes with an explicit annotation).
    """
    from pathlib import Path as _Path

    name_file, label_file = _Path(name_file), _Path(label_file)
    names = name_file.read_text().splitlines()
    raw_labels = label_file.read_text().splitlines()
    if len(names) != len(raw_labels):
        raise LabelParseError(
            f"{name_file} has {len(names)} lines but {label_file} has {len(raw_labels)} -- "
            "must be positionally paired 1:1"
        )

    records: dict[str, LabelRecord] = {}
    for name, raw_label in zip(names, raw_labels):
        name, raw_label = name.strip(), raw_label.strip()
        if not name:
            continue
        if raw_label not in ("0", "1"):
            raise LabelParseError(f"expected '0' or '1' in {label_file}, got {raw_label!r} for {name!r}")
        native_id = f"{vuln_class}/{name}"
        annotations = (Annotation(vuln_class=vuln_class),) if raw_label == "1" else ()
        records[native_id] = LabelRecord(native_id=native_id, granularity="file", annotations=annotations)
    return records
