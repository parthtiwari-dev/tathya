import pytest

from pipeline.processing.embedder import EMBEDDING_DIMENSION, passage_text, query_text, vector_literal


def test_e5_prefixes_are_applied() -> None:
    row = {"title": "RBI update", "raw_text": "Reserve Bank of India text."}

    assert passage_text(row).startswith("passage: RBI update")
    assert query_text(" RBI penalties ").startswith("query: RBI penalties")


def test_vector_literal_validates_dimension() -> None:
    literal = vector_literal([0.1] * EMBEDDING_DIMENSION)

    assert literal.startswith("[0.10000000")
    assert literal.endswith("]")

    with pytest.raises(ValueError):
        vector_literal([0.1])
