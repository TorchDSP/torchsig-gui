# SECURITY TESTS
# Tests that the server only answers requests addressed to the local machine

import pytest
from starlette.websockets import WebSocketDisconnect

@pytest.mark.parametrize('host', ['localhost', 'localhost:8000', '127.0.0.1', '127.0.0.1:8000'])
def test_allowed_host(affixed_client, host):
  # Requests addressed to the local machine should reach the API
  response = affixed_client.delete('/api/cancel-dataset/unknown_id', headers={ 'Host': host })
  assert response.status_code == 404

@pytest.mark.parametrize('host', ['example.com', 'attacker.example:8000', '0.0.0.0:8000', '192.168.0.10'])
def test_rejected_host(affixed_client, host):
  # Requests addressed to any other host name should be rejected before reaching the API
  response = affixed_client.delete('/api/cancel-dataset/unknown_id', headers={ 'Host': host })
  assert response.status_code == 400

def test_rejected_host_websocket(affixed_client):
  # Websocket connections addressed to other host names should be rejected
  with pytest.raises(WebSocketDisconnect):
    with affixed_client.websocket_connect('ws://attacker.example/ws') as websocket:
      websocket.receive_json()
