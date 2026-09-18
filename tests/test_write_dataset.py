# WRITE DATASET PROCEDURE TESTS
# Tests everything that goes into writing a dataset folder, its dataset files, and its YAML files

import json
import pytest
import time
from unittest.mock import patch

from conftest import TEST_DATA, measure_event_loop_gap, generate_test_dataset_file

from torchsiggui.app_write_dataset import create_dataset_file
from torchsiggui.files.file_io import SERVER_HOSTNAME
from torchsiggui.files.database_io import (
  run_query,
  queries,
  get_file_info
)

@patch('torchsiggui.app.create_dataset_file')
def test_post_write_dataset_response_success(mock_bg_task, affixed_client):
  # Send the post to the client with the JSON payload
  with open(TEST_DATA / 'data_default.json') as test_json_file:
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
  test_file_name = '/datasets/test_file'
  test_len = 10

  # Define the output data expected from the websocket
  def json_output(progress: int):
    return { 'type': 'file', 'update': { test_file_id: { 'current_status': '(' + str(progress) + '/' + str(test_len) + ') Generating...', 'progress': progress, 'total': test_len, 'filepath': test_file_name, 'complete': False, 'ready': False } } }

  # Connect to the websocket and simulate the triggers
  with affixed_client.websocket_connect('ws://localhost/ws') as websocket:
    # Trigger the file entry update
    await run_query(queries.add_file_entry, file_id=test_file_id, total=test_len, filepath=test_file_name)

    # The received data should contain a file update with the new file status
    data = websocket.receive_json()
    assert data == { 'type': 'file', 'update': { test_file_id: { 'current_status': '', 'progress': 0, 'total': test_len, 'filepath': test_file_name, 'complete': False, 'ready': False } } }

    # Trigger a sample file status update
    test_status = 'Test Status'
    await run_query(queries.update_current_status, file_id=test_file_id, new_status=test_status)

    # The received data should contain a file update with the updated file status
    data = websocket.receive_json()
    assert data == { 'type': 'file', 'update': { test_file_id: { 'current_status': test_status, 'progress': 0, 'total': test_len, 'filepath': test_file_name, 'complete': False, 'ready': False } } }

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
    assert data == { 'type': 'file', 'update': { test_file_id: { 'current_status': 'Complete', 'progress': test_len, 'total': test_len, 'filepath': test_file_name, 'complete': True, 'ready': True } } }

@pytest.mark.asyncio
async def test_post_write_dataset_function(affixed_client, affixed_dataset_location):
  # A dataset should not be present before the function runs
  file_info = await get_file_info()
  assert len(file_info) == 0
  assert not affixed_dataset_location.exists()

  # Get the JSON payload
  with open(TEST_DATA / 'data_default.json') as test_json_file:
    payload = json.load(test_json_file)

  # Create the dataset
  await create_dataset_file(payload)

  # The dataset should be written directly to <location>/<name>, with no archive, and marked ready
  file_info = await get_file_info()
  assert len(file_info) == 1
  test_file = next(iter(file_info.values()))
  dataset_folder = affixed_dataset_location.resolve() / payload['dataset']['root'].name
  assert test_file['filepath'] == str(dataset_folder)
  assert test_file['ready'] is True
  assert sorted(file.name for file in dataset_folder.iterdir()) == ['data.h5', 'dataset_info.yaml', 'writer_info.yaml']
  assert sorted(file.name for file in affixed_dataset_location.iterdir()) == [dataset_folder.name]

@pytest.mark.asyncio
async def test_post_write_dataset_chosen_location(affixed_client, tmp_path):
  # Get the JSON payload and choose a save location
  with open(TEST_DATA / 'data_default.json') as test_json_file:
    payload = json.load(test_json_file)
  location = tmp_path / 'chosen'
  location.mkdir()
  payload['dataset']['location'] = str(location)

  # The dataset should be written inside the chosen location
  await create_dataset_file(payload)
  assert (location.resolve() / 'test_tmp' / 'data.h5').is_file()

@patch('torchsiggui.app.create_dataset_file')
def test_post_write_dataset_home_location(mock_bg_task, affixed_client, tmp_path, monkeypatch):
  # A location starting with ~ should be expanded to the home folder of the account running the server
  monkeypatch.setenv('HOME', str(tmp_path))
  monkeypatch.setenv('USERPROFILE', str(tmp_path))
  (tmp_path / 'data').mkdir()
  with open(TEST_DATA / 'data_default.json') as test_json_file:
    payload = json.load(test_json_file)
  payload['dataset']['location'] = '~/data'

  response = affixed_client.post('/api/write-dataset', json=payload)
  assert response.status_code == 200
  mock_bg_task.assert_called_once()
  assert mock_bg_task.call_args.args[0]['dataset']['root'] == (tmp_path / 'data').resolve() / 'test_tmp'

@pytest.mark.parametrize('location, message', [
  ('relative/folder', 'must be a full path'),
  ('   ', 'Enter a save location'),
  ('MISSING', 'is not a folder'),
  ('FILE', 'is not a folder'),
])
@patch('torchsiggui.app.create_dataset_file')
def test_post_write_dataset_invalid_location(mock_bg_task, affixed_client, tmp_path, location, message):
  # Replace the placeholders with a missing folder and a file
  (tmp_path / 'file.txt').write_text('')
  location = { 'MISSING': str(tmp_path / 'missing'), 'FILE': str(tmp_path / 'file.txt') }.get(location, location)

  # Get the JSON payload and set the save location
  with open(TEST_DATA / 'data_default.json') as test_json_file:
    payload = json.load(test_json_file)
  payload['dataset']['location'] = location

  # The request should be rejected with a message that names the server, and nothing should be created
  response = affixed_client.post('/api/write-dataset', json=payload)
  assert response.status_code == 400
  assert message in response.json()['detail']
  assert SERVER_HOSTNAME in response.json()['detail']
  assert not (tmp_path / 'missing').exists()
  mock_bg_task.assert_not_called()

@patch('torchsiggui.app.create_dataset_file')
def test_post_write_dataset_existing_folder_without_overwrite(mock_bg_task, affixed_client, affixed_dataset_location):
  # Create a folder with the same name as the dataset
  existing = affixed_dataset_location / 'test_tmp'
  existing.mkdir(parents=True)
  (existing / 'keep.txt').write_text('keep')

  # With overwrite off, the request should be rejected and the folder left alone
  with open(TEST_DATA / 'data_default.json') as test_json_file:
    payload = json.load(test_json_file)
  payload['dataset']['overwrite'] = False
  response = affixed_client.post('/api/write-dataset', json=payload)
  assert response.status_code == 409
  assert 'already exists' in response.json()['detail']
  assert (existing / 'keep.txt').read_text() == 'keep'
  mock_bg_task.assert_not_called()

@patch('torchsiggui.app.create_dataset_file')
def test_post_write_dataset_existing_folder_not_dataset(mock_bg_task, affixed_client, affixed_dataset_location):
  # Create a folder with the same name as the dataset that is not a TorchSig dataset
  existing = affixed_dataset_location / 'test_tmp'
  existing.mkdir(parents=True)
  (existing / 'keep.txt').write_text('keep')

  # Even with overwrite on, the request should be rejected, since TorchSig would delete the folder
  with open(TEST_DATA / 'data_default.json') as test_json_file:
    payload = json.load(test_json_file)
  payload['dataset']['overwrite'] = True
  response = affixed_client.post('/api/write-dataset', json=payload)
  assert response.status_code == 400
  assert 'not a TorchSig dataset' in response.json()['detail']
  assert (existing / 'keep.txt').read_text() == 'keep'
  mock_bg_task.assert_not_called()

@pytest.mark.asyncio
async def test_post_write_dataset_overwrite_existing_dataset(affixed_client, affixed_dataset_location):
  # Write a dataset, then remove it from the list, keeping its files
  test_file_id = await generate_test_dataset_file(TEST_DATA / 'data_default.json')
  await run_query(queries.delete_file_entry, file_id=test_file_id)

  # With overwrite on, a dataset with the same name should replace it
  with open(TEST_DATA / 'data_default.json') as test_json_file:
    payload = json.load(test_json_file)
  payload['dataset']['overwrite'] = True
  await create_dataset_file(payload)

  file_info = await get_file_info()
  assert [file['ready'] for file in file_info.values()] == [True]
  assert (affixed_dataset_location.resolve() / 'test_tmp' / 'data.h5').is_file()
@patch('torchsiggui.app.create_dataset_file')
def test_post_write_dataset_duplicate_name(mock_bg_task, affixed_client):
  # Get the JSON payload
  with open(TEST_DATA / 'data_default.json') as test_json_file:
    payload = json.load(test_json_file)

  # The first request with a name should succeed
  response = affixed_client.post('/api/write-dataset', json=payload)
  assert response.status_code == 200

  # A second request with the same name should be rejected without starting a background task
  response = affixed_client.post('/api/write-dataset', json=payload)
  assert response.status_code == 409
  assert 'already exists' in response.json()['detail']
  mock_bg_task.assert_called_once()

@patch('torchsiggui.app.create_dataset_file')
def test_post_write_dataset_duplicate_name_different_case(mock_bg_task, affixed_client):
  # Get the JSON payload
  with open(TEST_DATA / 'data_default.json') as test_json_file:
    payload = json.load(test_json_file)

  # The first request with a name should succeed
  response = affixed_client.post('/api/write-dataset', json=payload)
  assert response.status_code == 200

  # A name that differs only in case should be rejected, since macOS and Windows file systems ignore case
  payload['dataset']['root'] = payload['dataset']['root'].swapcase()
  response = affixed_client.post('/api/write-dataset', json=payload)
  assert response.status_code == 409
  mock_bg_task.assert_called_once()

@pytest.mark.asyncio
@pytest.mark.parametrize('name', [
  '', '.', '..', '../escape', '/tmp/escape', 'nested/name', 'back\\slash', 123,
  'C:drive', 'stream:name', 'what?', 'star*', 'pipe|name', 'quote"name', 'less<name', 'tab\tname',
  'trailing.', 'trailing ', 'CON', 'nul', 'Com1', 'lpt9.data',
])
@patch('torchsiggui.app.create_dataset_file')
async def test_post_write_dataset_invalid_name(mock_bg_task, affixed_client, name):
  # Get the JSON payload and replace the dataset name
  with open(TEST_DATA / 'data_default.json') as test_json_file:
    payload = json.load(test_json_file)
  payload['dataset']['root'] = name

  # The request should be rejected
  response = affixed_client.post('/api/write-dataset', json=payload)
  assert response.status_code == 400
  assert 'Invalid dataset name' in response.json()['detail']

  # No file should be tracked and no background task should be started
  assert await get_file_info() == {}
  mock_bg_task.assert_not_called()

@patch('torchsiggui.app.create_dataset_file')
def test_post_write_dataset_missing_field(mock_bg_task, affixed_client):
  # Get the JSON payload and remove the dataset name
  with open(TEST_DATA / 'data_default.json') as test_json_file:
    payload = json.load(test_json_file)
  del payload['dataset']['root']

  # The request should be rejected
  response = affixed_client.post('/api/write-dataset', json=payload)
  assert response.status_code == 400
  assert 'root' in response.json()['detail']
  mock_bg_task.assert_not_called()

@pytest.mark.asyncio
async def test_post_write_dataset_function_failure(affixed_client):
  # Get the JSON payload
  with open(TEST_DATA / 'data_default.json') as test_json_file:
    payload = json.load(test_json_file)

  # Create the dataset file with a dataset builder that fails
  with patch('torchsiggui.app_write_dataset.torchsig_custom_dataset', side_effect=RuntimeError('Test Failure')):
    await create_dataset_file(payload)

  # The file should be marked complete, with the error as its status, and not ready to use
  file_info = await get_file_info()
  assert len(file_info) == 1
  test_file_id, test_file = next(iter(file_info.items()))
  assert test_file['current_status'] == 'Test Failure'
  assert test_file['ready'] is False
  assert await run_query(queries.get_is_complete, file_id=test_file_id)

@pytest.mark.parametrize('endpoint', ['/api/write-dataset', '/api/write-sample'])
@patch('torchsiggui.app.create_sample_image')
@patch('torchsiggui.app.create_dataset_file')
def test_post_write_invalid_content_type(mock_dataset_task, mock_sample_task, affixed_client, endpoint):
  # Send the JSON payload labelled as plain text
  with open(TEST_DATA / 'data_default.json') as test_json_file:
    payload = test_json_file.read()
  response = affixed_client.post(endpoint, content=payload, headers={ 'Content-Type': 'text/plain' })

  # The request should be rejected with an error status, and nothing should be started
  assert response.status_code == 422
  mock_dataset_task.assert_not_called()
  mock_sample_task.assert_not_called()

@pytest.mark.parametrize('endpoint', ['/api/write-dataset', '/api/write-sample'])
@patch('torchsiggui.app.create_sample_image')
@patch('torchsiggui.app.create_dataset_file')
def test_post_write_json_with_charset(mock_dataset_task, mock_sample_task, affixed_client, endpoint):
  # Send the JSON payload with a charset in its content type
  with open(TEST_DATA / 'data_default.json') as test_json_file:
    payload = test_json_file.read()
  response = affixed_client.post(endpoint, content=payload, headers={ 'Content-Type': 'application/json; charset=utf-8' })

  # The request should be accepted
  assert response.status_code == 200
  assert response.json() == { 'message': 'success' }

@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_post_write_dataset_function_does_not_block(affixed_client):
  # Get the JSON payload
  with open(TEST_DATA / 'data_default.json') as test_json_file:
    payload = json.load(test_json_file)

  # Define a slow dataset builder that blocks its thread, then fails
  def slow_build(*args, **kwargs):
    time.sleep(1)
    raise RuntimeError('Test Failure')

  # Write the dataset while measuring the longest time the event loop goes without running other tasks
  with patch('torchsiggui.app_write_dataset.torchsig_custom_dataset', side_effect=slow_build):
    max_gap = await measure_event_loop_gap(create_dataset_file(payload))

  # The event loop should keep running other tasks while the dataset is built
  assert max_gap < 0.5
