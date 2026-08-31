import pytest

from forge_cli.protocol_resolution import resolve_effective_review_profile


@pytest.mark.parametrize("floor", ["focused", "standard", "strict"])
@pytest.mark.parametrize("mode", ["recommended", "fast"])
def test_recommended_and_fast_never_rank_below_the_floor(floor: str, mode: str) -> None:
    assert resolve_effective_review_profile(floor, mode) == floor


@pytest.mark.parametrize(
    ("floor", "expected"),
    [
        ("focused", "standard"),
        ("standard", "strict"),
        ("strict", "strict"),
    ],
)
def test_thorough_steps_up_one_rank_capped_at_strict(floor: str, expected: str) -> None:
    assert resolve_effective_review_profile(floor, "thorough") == expected
