from unittest.mock import patch

import pytest
from django.db.utils import OperationalError
from django.urls import reverse


@pytest.mark.django_db
def test_health_check_ok(client):
    response = client.get(reverse("health-check"))

    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
    assert "environment" in body
    assert "version" in body


@pytest.mark.django_db
def test_health_check_db_unreachable(client):
    with patch("addons.health.connections") as mock_connections:
        mock_connections.__getitem__.return_value.cursor.side_effect = OperationalError(
            "could not connect to server"
        )
        response = client.get(reverse("health-check"))

    assert response.status_code == 503

    body = response.json()
    assert body["status"] == "error"
    assert body["database"] == "unreachable"
