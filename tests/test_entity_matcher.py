from pipeline.processing.entity_matcher import match_entities


def test_match_entities_uses_aliases_and_word_boundaries() -> None:
    matches = match_entities("The RBI and Finance Ministry issued an update.")
    names = {match.name for match in matches}

    assert "Reserve Bank of India" in names
    assert "Ministry of Finance" in names


def test_match_entities_does_not_match_substrings() -> None:
    matches = match_entities("This talks about orbit and merit only.")

    assert "Reserve Bank of India" not in {match.name for match in matches}


def test_match_entities_includes_seeded_public_actors() -> None:
    matches = match_entities("Sonam Wangchuk and Anna Hazare appealed to PM Modi.")
    names = {match.name for match in matches}

    assert "Sonam Wangchuk" in names
    assert "Anna Hazare" in names
    assert "Narendra Modi" in names
