# DOWNLOAD TESTS
# Tests that the generated archive files can be downloaded and cancelled

import pytest

from torchsig.utils.file_handlers.hdf5 import HDF5Reader

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
  test_file_id = await affixed_test_dataset_file

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
  signal = reader.read(0)
  reader.teardown()

@pytest.mark.asyncio
async def test_delete_cancel_dataset_response_success(affixed_client, affixed_test_dataset_file):
  # Define the input data for the websocket trigger functions
  test_file_id = await affixed_test_dataset_file

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
  test_file_id = await affixed_test_dataset_file

  # Define the output data expected from the websocket
  def json_output():
    return { 'type': 'file', 'update': {} }

  # Connect to the websocket and simulate the triggers
  with affixed_client.websocket_connect('/ws') as websocket:
    # The first connection to the websocket should return the non-empty file status
    data_before_delete = websocket.receive_json()
    assert data_before_delete != json_output()

    # Trigger the file deletion update
    await run_query(queries.delete_file_entry, file_id=test_file_id)

    # The received data should contain a file update with no file entries
    data_after_delete = websocket.receive_json()
    assert data_after_delete == json_output()