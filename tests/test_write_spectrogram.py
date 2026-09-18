# WRITE SPECTROGRAM PROCEDURE TESTS
# Tests everything that goes into creating and sending a spectrogram image file

import json
import matplotlib
import pytest
import time
from unittest.mock import patch

from conftest import TEST_DATA, measure_event_loop_gap

from torchsiggui.files.file_io import DATASET_FOLDER
from torchsiggui.app_write_spectrogram import create_sample_image
from torchsiggui.files.database_io import (
  run_query,
  queries
)

@patch('torchsiggui.app.create_sample_image')
def test_post_write_sample_response_success(mock_bg_task, affixed_client):
  # Send the post to the client with the JSON payload
  with open(TEST_DATA / 'data_default.json') as test_json_file:
    payload = json.load(test_json_file)
  response = affixed_client.post('/api/write-sample', json=payload)

  # The correct response should be returned
  assert response.status_code == 200
  assert response.json() == { 'message': 'success' }

  # The background process should be started after the call completes
  mock_bg_task.assert_called_once()

@pytest.mark.timeout(5)
@pytest.mark.asyncio
async def test_post_write_sample_websocket_success(affixed_client):
  # Define the input data for the websocket trigger functions
  test_image_name = 'test_image.png'

  # Define the output data expected from the websocket
  def json_output():
    return { 'type': 'spectrogram', 'update': test_image_name }

  # Connect to the websocket and simulate the triggers
  with affixed_client.websocket_connect('ws://localhost/ws') as websocket:
    # Trigger the spectrogram update
    await run_query(queries.update_start_spectrogram, new_name=test_image_name)
    await run_query(queries.update_complete_spectrogram)

    # The received data should contain a spectrogram update with the new image name
    data = websocket.receive_json()
    assert data == json_output()

@pytest.mark.asyncio
async def test_post_write_sample_function(affixed_client):
  # An image file should not be present before the function runs
  spectrogram_filename = await run_query(queries.get_spectrogram_details)
  assert not spectrogram_filename['current_name']

  images = [file for file in DATASET_FOLDER.iterdir() if file.suffix == '.png']
  assert not images

  # Get the JSON payload
  with open(TEST_DATA / 'data_default.json') as test_json_file:
    payload = json.load(test_json_file)

  # Create the image file
  assert DATASET_FOLDER.exists()
  await create_sample_image(payload)

  # An image file should be created
  spectrogram_filename = await run_query(queries.get_spectrogram_details)
  assert spectrogram_filename['current_name']

  images = [file for file in DATASET_FOLDER.iterdir() if file.suffix == '.png']
  assert images
def test_matplotlib_uses_agg_backend():
  # The server should plot with the non-interactive Agg backend, since it may run without a display
  assert matplotlib.get_backend().lower() == 'agg'

@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_post_write_sample_function_does_not_block(affixed_client):
  # Get the JSON payload
  with open(TEST_DATA / 'data_default.json') as test_json_file:
    payload = json.load(test_json_file)

  # Define a slow dataset builder that blocks its thread, then fails
  def slow_build(*args, **kwargs):
    time.sleep(1)
    raise RuntimeError('Test Failure')

  # Create the image while measuring the longest time the event loop goes without running other tasks
  with patch('torchsiggui.app_write_spectrogram.torchsig_custom_dataset', side_effect=slow_build):
    max_gap = await measure_event_loop_gap(create_sample_image(payload))

  # The event loop should keep running other tasks while the sample is built
  assert max_gap < 0.5
