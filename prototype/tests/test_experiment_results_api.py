from fastapi.testclient import TestClient
from prototype.api import app


def test_experiment_results_valid_shape():
    response = TestClient(app).get('/api/experiment-results')
    assert response.status_code == 200
    data = response.json()
    assert {'available','source','run_id','optimisers','baselines'} <= set(data)
    assert data['source'] in ('new_official_full_run','no_verified_full_run')


def test_health_endpoint():
    response = TestClient(app).get('/api/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'