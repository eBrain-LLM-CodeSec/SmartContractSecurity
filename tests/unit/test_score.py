from a4v.commentator import Comment
from a4v.features import NodeFeatures
from a4v.score import Candidate, dynamic_threshold, is_strong_signal


def _features(**kwargs) -> NodeFeatures:
    base = dict(node_id="x", cyclomatic_complexity=1.0, external_call_count=0.0,
                unsafe_cast_count=0.0, write_after_external_call_count=0.0)
    base.update(kwargs)
    return NodeFeatures(**base)


def test_dynamic_threshold_percentile_picks_expected_set():
    candidates = [
        Candidate(node_id=f"n{i}", score=score, strong_signal=False, features=_features(node_id=f"n{i}"))
        for i, score in enumerate([10.0, 8.0, 6.0, 4.0, 2.0, 0.0])
    ]
    dynamic_threshold(candidates, mode="percentile", percentile=0.7)
    kept = {c.node_id for c in candidates if c.kept}
    # 70th percentile of [0,2,4,6,8,10] is 7.0 -> only scores >= 7.0 survive: 10, 8
    assert kept == {"n0", "n1"}


def test_strong_signal_candidate_survives_high_threshold():
    weak = Candidate(node_id="weak", score=0.1, strong_signal=False, features=_features())
    strong = Candidate(
        node_id="strong", score=0.05, strong_signal=True,
        features=_features(write_after_external_call_count=1.0),
    )
    high_score_but_not_strong = Candidate(node_id="hi", score=100.0, strong_signal=False, features=_features())

    candidates = [weak, strong, high_score_but_not_strong]
    dynamic_threshold(candidates, mode="percentile", percentile=0.99)

    assert strong.kept, "strong-signal candidate must never be dropped by the threshold"
    assert high_score_but_not_strong.kept
    assert not weak.kept


def test_is_strong_signal_write_after_external_call():
    f = _features(write_after_external_call_count=1.0)
    assert is_strong_signal(f, comment=None)


def test_is_strong_signal_unsafe_cast():
    f = _features(unsafe_cast_count=1.0)
    assert is_strong_signal(f, comment=None)


def test_is_strong_signal_commentator_high_severity():
    f = _features()
    comment = Comment(suspicious=True, vuln_class="reentrancy", severity="high", rationale="x", lines=[1])
    assert is_strong_signal(f, comment)


def test_is_strong_signal_false_for_low_severity_and_no_static_signal():
    f = _features()
    comment = Comment(suspicious=True, vuln_class="other", severity="low", rationale="x", lines=[1])
    assert not is_strong_signal(f, comment)
