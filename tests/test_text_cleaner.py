from pipeline.processing.text_cleaner import clean_source_text


def test_clean_source_text_removes_markup_and_unescapes_entities() -> None:
    assert clean_source_text("<p>A&nbsp;B &amp; C</p>") == "A B & C"
