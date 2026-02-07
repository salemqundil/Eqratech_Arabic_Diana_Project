import pytest

from fvafk.c1.segment_inventory import ConsonantInventory


def test_consonant_inventory_has_30_entries():
    assert len(ConsonantInventory.CONSONANTS) == 30


@pytest.mark.parametrize("consonant, expected_feature", [
    ("ب", "manner:stop"),
    ("ط", "emphatic"),
    ("ض", "voice:voiced"),
    ("ة", "manner:marker"),
])
def test_get_features_contains_expected(consonant, expected_feature):
    features = ConsonantInventory.get_features(consonant)
    assert expected_feature in features
