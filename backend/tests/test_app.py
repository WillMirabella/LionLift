# Tests that the Flask app starts and every blueprint is registered


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_example_route(client):
    response = client.get("/api/example/")
    assert response.status_code == 200
    assert response.get_json() == {"exampleData": "test_success"}


def test_expected_routes_exist(client):
    rules = {rule.rule for rule in client.application.url_map.iter_rules()}
    for expected in ("/", "/api/example/", "/api/auth/request-code", "/api/auth/verify"):
        assert expected in rules


def test_unknown_route_is_404(client):
    assert client.get("/api/does-not-exist").status_code == 404
