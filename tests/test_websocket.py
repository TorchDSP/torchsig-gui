# WEBSOCKET TESTS
# Tests the lifecycle of the websocket that streams file and spectrogram updates

import asyncio
import time
from unittest.mock import patch

def test_websocket_tasks_stop_on_disconnect(affixed_client):
  # Record the feed tasks the websocket starts
  created_tasks = []
  real_create_task = asyncio.create_task
  def record_task(coro):
    task = real_create_task(coro)
    created_tasks.append(task)
    return task

  with patch('torchsiggui.app.create_task', side_effect=record_task):
    # Connect to the websocket, then disconnect
    with affixed_client.websocket_connect('ws://localhost/ws'):
      pass

    # Wait for the server to handle the disconnect
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and not (len(created_tasks) == 2 and all(task.done() for task in created_tasks)):
      time.sleep(0.05)

  # Both feed tasks should be stopped
  assert len(created_tasks) == 2
  assert all(task.cancelled() for task in created_tasks)
