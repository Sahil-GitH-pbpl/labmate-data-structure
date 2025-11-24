from datetime import datetime, timedelta


def test_smoke_flow(client):
    token = "alice"
    # create ticket
    resp = client.post(
        "/infra/create",
        headers={"Authorization": f"Bearer {token}"},
        data={
            "category": "Hardware",
            "subcategory": "Desktop",
            "department": "Ops",
            "description": "PC not working",
        },
    )
    assert resp.status_code == 200
    ticket_id = resp.json()["ticket_id"]

    # list my
    resp = client.get("/infra/my", headers={"Authorization": f"Bearer {token}"})
    assert any(t["ticket_id"] == ticket_id for t in resp.json()["items"])

    # pick ticket
    commitment = (datetime.utcnow() + timedelta(hours=4)).isoformat()
    resp = client.post(
        f"/infra/pick/{ticket_id}",
        headers={"Authorization": "Bearer bob"},
        json={"commitment_time": commitment},
    )
    assert resp.status_code == 200

    # add update
    resp = client.post(
        f"/infra/update/{ticket_id}",
        headers={"Authorization": "Bearer bob"},
        json={"note": "Investigating", "status": "In Progress"},
    )
    assert resp.status_code == 200

    # resolve
    resp = client.post(
        f"/infra/resolve/{ticket_id}",
        headers={"Authorization": "Bearer bob"},
        json={"note": "Fixed"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "Resolved"
