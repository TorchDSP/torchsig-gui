# CANCEL DATASET TESTS
# Tests that unfinished datasets can be cancelled and deleted, and finished datasets can be removed from the list

import json
import pytest
import yaml
from pathlib import Path
from unittest.mock import patch

from conftest import TEST_DATA

from torchsiggui.app_write_dataset import create_dataset_file
from torchsiggui.files.database_io import (
  run_query,
  queries,
  get_file_info
)

@pytest.mark.asyncio
async def test_remove_finished_dataset_keeps_files(affixed_client, affixed_test_dataset_file):
  # Get the folder of the finished dataset
  test_file_id = affixed_test_dataset_file
  dataset_folder = (await get_file_info())[test_file_id]['filepath']

  # Removing a finished dataset should succeed
  response = affixed_client.delete('/api/cancel-dataset/' + test_file_id)
  assert response.status_code == 200
  assert response.json() == { 'message': 'success' }

  # The dataset should leave the list, but its files should be kept where the user saved them
  assert await get_file_info() == {}
  assert (Path(dataset_folder) / 'data.h5').is_file()

@pytest.mark.timeout(5)
@pytest.mark.asyncio
async def test_remove_dataset_websocket_success(affixed_client, affixed_test_dataset_file):
  # Connect to the websocket and simulate the triggers
  with affixed_client.websocket_connect('ws://localhost/ws') as websocket:
    # The first connection to the websocket should return the non-empty file status
    data_before_delete = websocket.receive_json()
    assert data_before_delete != { 'type': 'file', 'update': {} }

    # Trigger the file deletion update
    await run_query(queries.delete_file_entry, file_id=affixed_test_dataset_file)

    # The received data should contain a file update with no file entries
    data_after_delete = websocket.receive_json()
    assert data_after_delete == { 'type': 'file', 'update': {} }

@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_cancel_unfinished_dataset_deletes_folder(affixed_client, affixed_dataset_location):
  # Create a partial dataset folder, as TorchSig leaves it while writing
  dataset_folder = affixed_dataset_location / 'partial'
  dataset_folder.mkdir(parents=True)
  (dataset_folder / 'data.h5').write_bytes(b'partial')
  (dataset_folder / 'writer_info.yaml').write_text(yaml.safe_dump({ 'complete': False }))

  # Add a file entry for it whose write has stopped without finishing
  test_file_id = 'test_id'
  await run_query(queries.add_file_entry, file_id=test_file_id, total=10, filepath=str(dataset_folder))
  await run_query(queries.fail_file, file_id=test_file_id, error_status='Test Failure')

  # Cancelling should delete the partial dataset folder, but not the save location
  response = affixed_client.delete('/api/cancel-dataset/' + test_file_id)
  assert response.status_code == 200
  assert await get_file_info() == {}
  assert not dataset_folder.exists()
  assert affixed_dataset_location.is_dir()

@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_cancel_failed_dataset(affixed_client, affixed_dataset_location):
  # Get the JSON payload
  with open(TEST_DATA / 'data_default.json') as test_json_file:
    payload = json.load(test_json_file)

  # Create a dataset whose write fails
  with patch('torchsiggui.app_write_dataset.torchsig_custom_dataset', side_effect=RuntimeError('Test Failure')):
    await create_dataset_file(payload)
  test_file_id = list((await get_file_info()).keys())[0]

  # Cancelling the failed dataset should finish instead of waiting forever
  response = affixed_client.delete('/api/cancel-dataset/' + test_file_id)
  assert response.status_code == 200
  assert response.json() == { 'message': 'success' }

  # The failed dataset should be removed, and the save location kept
  assert await get_file_info() == {}
  assert list(affixed_dataset_location.iterdir()) == []

@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_cancel_failed_overwrite_keeps_finished_dataset(affixed_client, affixed_test_dataset_file):
  # Remove the finished dataset from the list, keeping its files
  dataset_folder = Path((await get_file_info())[affixed_test_dataset_file]['filepath'])
  affixed_client.delete('/api/cancel-dataset/' + affixed_test_dataset_file)

  # Try to overwrite it with a dataset that fails before writing starts
  with open(TEST_DATA / 'data_default.json') as test_json_file:
    payload = json.load(test_json_file)
  payload['dataset']['overwrite'] = True
  with patch('torchsiggui.app_write_dataset.torchsig_custom_dataset', side_effect=RuntimeError('Test Failure')):
    await create_dataset_file(payload)
  test_file_id = list((await get_file_info()).keys())[0]

  # Cancelling the failed dataset should keep the finished dataset it did not replace
  response = affixed_client.delete('/api/cancel-dataset/' + test_file_id)
  assert response.status_code == 200
  assert (dataset_folder / 'data.h5').is_file()

def test_cancel_dataset_unknown_id(affixed_client):
  # A cancel for an unknown file id should not be found
  response = affixed_client.delete('/api/cancel-dataset/unknown_id')
  assert response.status_code == 404
