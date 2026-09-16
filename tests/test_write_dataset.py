# WRITE DATASET PROCEDURE TESTS
# Tests everything that goes into writing a dataset file, its associated YAML files, and the archive file containing them all

import json
import pytest
from unittest.mock import patch

from torchsiggui.app_write_dataset import create_dataset_file
from torchsiggui.files.file_io import get_archive_extension, DATASET_FOLDER
from torchsiggui.files.database_io import (
  run_query,
  queries,
  get_file_info
)

@patch('torchsiggui.app.create_dataset_file')
def test_post_write_dataset_response_success(mock_bg_task, affixed_client):
  # Send the post to the client with the JSON payload
  with open('./test_data/data_default.json') as test_json_file:
    payload = json.load(test_json_file)
  response = affixed_client.post('/api/write-dataset', json=payload)

  # The correct response should be returned
  assert response.status_code == 200
  assert response.json() == { 'message': 'success' }

  # The background process should be started after the call completes
  mock_bg_task.assert_called_once()

@pytest.mark.timeout(5)
@pytest.mark.asyncio
async def test_post_write_dataset_websocket_success(affixed_client, subtests):
  # Define the input data for the websocket trigger functions
  test_file_id = 'test_id'
  test_file_name = 'test_file' + '.' + get_archive_extension()
  test_len = 10

  # Define the output data expected from the websocket
  def json_output(progress: int):
    return { 'type': 'file', 'update': { test_file_id: { 'current_status': '(' + str(progress) + '/' + str(test_len) + ') Generating...', 'progress': progress, 'total': test_len, 'filepath': test_file_name } } }

  # Connect to the websocket and simulate the triggers
  with affixed_client.websocket_connect('/ws') as websocket:
    # Trigger the file entry update
    await run_query(queries.add_file_entry, file_id=test_file_id, total=test_len, filepath=test_file_name)

    # The received data should contain a file update with the new file status
    data = websocket.receive_json()
    assert data == { 'type': 'file', 'update': { test_file_id: { 'current_status': '', 'progress': 0, 'total': test_len, 'filepath': test_file_name } } }

    # Trigger a sample file status update
    test_status = 'Test Status'
    await run_query(queries.update_current_status, file_id=test_file_id, new_status=test_status)

    # The received data should contain a file update with the updated file status
    data = websocket.receive_json()
    assert data == { 'type': 'file', 'update': { test_file_id: { 'current_status': test_status, 'progress': 0, 'total': test_len, 'filepath': test_file_name } } }

    # Trigger the file progress updates
    for progress in range(1, test_len + 1):
      with subtests.test(msg='Dataset Websocket Test', progress=progress):
        # Trigger the next file progress update
        await run_query(queries.update_file_progress, file_id=test_file_id)

        # The received data should contain a file update with an updated progress
        data = websocket.receive_json()
        assert data == json_output(progress)

    # Trigger the file completion update
    await run_query(queries.complete_file, file_id=test_file_id, complete_status='Complete')

    # The received data should contain a file update with the completed file status
    data = websocket.receive_json()
    assert data == { 'type': 'file', 'update': { test_file_id: { 'current_status': 'Complete', 'progress': test_len, 'total': test_len, 'filepath': test_file_name } } }

@pytest.mark.asyncio
async def test_post_write_dataset_function(affixed_client):
  # A dataset file should not be present before the function runs
  file_info = await get_file_info()
  assert len(file_info) == 0

  datasets = [file for file in DATASET_FOLDER.iterdir() if file.suffix == '.' + get_archive_extension()]
  assert not datasets

  # Get the JSON payload
  with open('./test_data/data_default.json') as test_json_file:
    payload = json.load(test_json_file)

  # Create the dataset file
  assert DATASET_FOLDER.exists()
  await create_dataset_file(payload)

  # A dataset file should be created
  file_info = await get_file_info()
  assert len(file_info) > 0

  datasets = [file for file in DATASET_FOLDER.iterdir() if file.suffix == '.' + get_archive_extension()]
  assert datasets