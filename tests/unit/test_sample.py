from a4v.gnn.etl.extract import IndexRow
from a4v.gnn.etl.sample import stratified_sample


def _row(cid, merged_classes, pragma):
    return IndexRow(contract_id=cid, native_ids=[cid], merged_classes=merged_classes, pragma_major_minor=pragma)


def _synthetic_corpus():
    rows = []
    rows += [_row(f"reentrancy-{i}", ["reentrancy"], "0.8") for i in range(5)]
    rows += [_row(f"access-{i}", ["access_control"], "0.8") for i in range(3)]
    rows += [_row("multihot-1", ["reentrancy", "access_control"], "0.4")]  # multi-hot, rare pragma band
    rows += [_row(f"unlabeled-{i}", [], "0.8") for i in range(20)]
    rows += [_row(f"rare-{i}", ["rare_class"], "0.5") for i in range(2)]
    return rows


def _classes_of(rows_by_id, cid):
    row = rows_by_id[cid]
    return row.merged_classes or ["unlabeled"]


def test_every_non_empty_cell_is_represented():
    rows = _synthetic_corpus()
    rows_by_id = {r.contract_id: r for r in rows}
    result = stratified_sample(rows, target_n=10, seed=0, floor_per_cell=1)

    represented_classes = set()
    for cid in result.contract_ids:
        represented_classes.update(_classes_of(rows_by_id, cid))

    assert {"reentrancy", "access_control", "unlabeled", "rare_class"} <= represented_classes


def test_multihot_contract_counted_in_all_its_cells():
    rows = _synthetic_corpus()
    result = stratified_sample(rows, target_n=10, seed=0)
    assert result.cell_counts["reentrancy|0.4"] == 1
    assert result.cell_counts["access_control|0.4"] == 1


def test_output_is_exactly_target_n_unique_ids():
    rows = _synthetic_corpus()
    result = stratified_sample(rows, target_n=10, seed=0)
    assert len(result.contract_ids) == 10
    assert len(set(result.contract_ids)) == 10


def test_seed_reproducible():
    rows = _synthetic_corpus()
    r1 = stratified_sample(rows, target_n=10, seed=42)
    r2 = stratified_sample(rows, target_n=10, seed=42)
    assert r1.contract_ids == r2.contract_ids


def test_unlabeled_does_not_crowd_out_rare_labeled_classes():
    # 20 unlabeled vs. 2 rare_class members -- rare_class must still show up
    # in a target_n=10 sample instead of being drowned out by raw volume.
    rows = _synthetic_corpus()
    rows_by_id = {r.contract_id: r for r in rows}
    result = stratified_sample(rows, target_n=10, seed=0)
    assert any(_classes_of(rows_by_id, cid) == ["rare_class"] for cid in result.contract_ids)


def test_sample_capped_at_corpus_size_when_target_exceeds_it():
    rows = _synthetic_corpus()
    result = stratified_sample(rows, target_n=10_000, seed=0)
    assert len(result.contract_ids) == len(rows)


def test_empty_corpus_returns_empty_sample():
    result = stratified_sample([], target_n=200, seed=0)
    assert result.contract_ids == []
    assert result.cell_counts == {}
