import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.main import app, get_repository


def test_api_serves_topics_and_corrections() -> None:
    class Repository:
        def list_topics(self, limit):
            assert limit == 2
            return [{"id": "topic-id", "title": "Reserve Bank of India"}]

        def topic_detail(self, topic_id):
            assert topic_id == "topic-id"
            return {"topic": {"id": topic_id}, "claims": [], "events": [], "verifiable_facts": [], "relations": []}

        def create_correction(self, target_table, target_row_id, issue_description):
            return {"id": "correction-id", "target_table": target_table, "target_row_id": target_row_id, "issue_description": issue_description}

    app.dependency_overrides[get_repository] = lambda: Repository()
    client = TestClient(app)
    try:
        assert client.get("/health").json() == {"status": "ok"}
        assert client.get("/topics?limit=2").json()["topics"][0]["title"] == "Reserve Bank of India"
        assert client.get("/topics/topic-id").json()["topic"]["id"] == "topic-id"
        response = client.post(
            "/corrections",
            json={"target_table": "claims", "target_row_id": "claim-id", "issue_description": "quoted span looks wrong"},
        )
        assert response.status_code == 201
        assert response.json()["id"] == "correction-id"
    finally:
        app.dependency_overrides.clear()
