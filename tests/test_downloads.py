# DOWNLOAD TESTS
# Tests that the generated archive files can be downloaded and cancelled

import json
import pytest
from unittest.mock import patch

from conftest import TEST_DATA

from torchsig.utils.file_handlers.hdf5 import HDF5Reader

from torchsiggui.app_write_dataset import create_dataset_file
from torchsiggui.files.file_io import (
  DATASET_FOLDER,
  get_archive_extension,
  extract_archive_file
)
from torchsiggui.files.database_io import (
  run_query,
  queries,
  get_file_info
)

@pytest.mark.asyncio
async def test_get_download_dataset_response_success(affixed_client, affixed_test_dataset_file):
  # Define the input data for the websocket trigger functions
  test_file_id = affixed_test_dataset_file

  # A dataset file should be present before the function runs
  file_info = await get_file_info()
  assert len(file_info) > 0

  datasets = [file for file in DATASET_FOLDER.iterdir() if file.suffix == '.' + get_archive_extension()]
  assert datasets

  # Get the dataset file directory by the id
  test_filepath = file_info[test_file_id]['filepath']
  test_folder = test_filepath[:test_filepath.rfind('.')]

  # Send the GET request to the client with the dataset id
  response = affixed_client.get('/api/download-dataset/' + test_file_id)

  # The file should be returned
  assert response.status_code == 200

  assert "application/octet-stream" in response.headers.get("content-type", "")
  assert "attachment" in response.headers.get("content-disposition", "")

  # The download should be an archive file with other files inside
  archive_path = DATASET_FOLDER / ('archive.' + get_archive_extension())
  with open(archive_path, 'wb') as f:
    f.write(response.content)

  extract_archive_file(archive_path, DATASET_FOLDER)

  # The file inside should be a HDF5 file
  reader = HDF5Reader(DATASET_FOLDER / test_folder)
  reader.read(0)
  reader.teardown()

@pytest.mark.asyncio
async def test_delete_cancel_dataset_response_success(affixed_client, affixed_test_dataset_file):
  # Define the input data for the websocket trigger functions
  test_file_id = affixed_test_dataset_file

  # A dataset file should be present before the function runs
  file_info = await get_file_info()
  assert len(file_info) > 0

  datasets = [file for file in DATASET_FOLDER.iterdir() if file.suffix == '.' + get_archive_extension()]
  assert datasets

  # Send the DELETE request to the client with the dataset id
  response = affixed_client.delete('/api/cancel-dataset/' + test_file_id)

  # The correct response should be returned
  assert response.status_code == 200
  assert response.json() == { 'message': 'success' }

  # A dataset file should not be present after the function runs
  file_info = await get_file_info()
  assert len(file_info) == 0

  datasets = [file for file in DATASET_FOLDER.iterdir() if file.suffix == '.' + get_archive_extension()]
  assert not datasets

@pytest.mark.timeout(5)
@pytest.mark.asyncio
async def test_delete_cancel_dataset_websocket_success(affixed_client, affixed_test_dataset_file):
  # Define the input data for the websocket trigger functions
  test_file_id = affixed_test_dataset_file

  # Define the output data expected from the websocket
  def json_output():
    return { 'type': 'file', 'update': {} }

  # Connect to the websocket and simulate the triggers
  with affixed_client.websocket_connect('ws://localhost/ws') as websocket:
    # The first connection to the websocket should return the non-empty file status
    data_before_delete = websocket.receive_json()
    assert data_before_delete != json_output()

    # Trigger the file deletion update
    await run_query(queries.delete_file_entry, file_id=test_file_id)

    # The received data should contain a file update with no file entries
    data_after_delete = websocket.receive_json()
    assert data_after_delete == json_output()
@pytest.mark.asyncio
async def test_get_download_dataset_not_ready(affixed_client):
  # Add a file entry that is still being written
  test_file_id = 'test_id'
  await run_query(queries.add_file_entry, file_id=test_file_id, total=10, filepath='test_file.' + get_archive_extension())

  # The download should be refused until the archive is ready
  response = affixed_client.get('/api/download-dataset/' + test_file_id)
  assert response.status_code == 409

@pytest.mark.asyncio
async def test_get_download_dataset_missing_archive(affixed_client):
  # Add a file entry that is marked ready, but has no archive file
  test_file_id = 'test_id'
  await run_query(queries.add_file_entry, file_id=test_file_id, total=10, filepath='test_file.' + get_archive_extension())
  await run_query(queries.complete_file, file_id=test_file_id, complete_status='Complete')

  # The download should report the missing file instead of failing mid-stream
  response = affixed_client.get('/api/download-dataset/' + test_file_id)
  assert response.status_code == 404

def test_get_download_dataset_unknown_id(affixed_client):
  # A download for an unknown file id should not be found
  response = affixed_client.get('/api/download-dataset/unknown_id')
  assert response.status_code == 404

def test_delete_cancel_dataset_unknown_id(affixed_client):
  # A cancel for an unknown file id should not be found
  response = affixed_client.delete('/api/cancel-dataset/unknown_id')
  assert response.status_code == 404

@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_delete_cancel_failed_dataset(affixed_client):
  # Get the JSON payload
  with open(TEST_DATA / 'data_default.json') as test_json_file:
    payload = json.load(test_json_file)

  # Create a dataset file whose write fails
  with patch('torchsiggui.app_write_dataset.torchsig_custom_dataset', side_effect=RuntimeError('Test Failure')):
    await create_dataset_file(payload)
  file_info = await get_file_info()
  test_file_id = list(file_info.keys())[0]

  # Cancelling the failed dataset should finish instead of waiting forever
  response = affixed_client.delete('/api/cancel-dataset/' + test_file_id)
  assert response.status_code == 200
  assert response.json() == { 'message': 'success' }

  # The failed dataset and its files should be removed
  assert await get_file_info() == {}
  assert not (DATASET_FOLDER / test_file_id).exists()
