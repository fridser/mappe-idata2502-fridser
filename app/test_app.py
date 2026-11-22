from app import app
def test_health_is_ok():
    response = app.test_client().get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"

def test_buy_rejects_get():
    assert app.test_client().get("/love/buy").status_code == 405