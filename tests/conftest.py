# PYTEST CONFTEST FILE
# Defines fixtures for common code chunks used in other tests

import os
import tempfile

# Keeps test data out of the user's real data folder, so tests never touch a running server's datasets
# - Must be set before torchsiggui is imported, since the data folder is resolved at import time
os.environ.setdefault('TORCHSIGGUI_DATA_DIR', tempfile.mkdtemp(prefix='torchsiggui-test-'))

from fastapi.testclient import TestClient  # noqa: E402

import asyncio  # noqa: E402
import json  # noqa: E402
import time  # noqa: E402
import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from pathlib import Path  # noqa: E402

from torchsiggui.main import create_app  # noqa: E402
from torchsiggui.app_write_dataset import create_dataset_file  # noqa: E402
from torchsiggui.files.database_io import get_file_info  # noqa: E402

# Resolves test data relative to this file so the tests run from any directory
TEST_DATA = Path(__file__).resolve().parent / 'test_data'

# UTILITY FUNCTIONS
# Generates a dataset file and returns the file id
async def generate_test_dataset_file(json_filename):
  # Get the JSON payload
  with open(json_filename) as f:
    payload = json.load(f)

  # Create the dataset file
  await create_dataset_file(payload)

  # Define the file id for the dataset file
  file_info = await get_file_info()
  test_file_id = list(file_info.keys())[0]

  # Return the test file id
  return test_file_id

# Runs a coroutine and returns the longest time, in seconds, that the event loop went without running other tasks
async def measure_event_loop_gap(coroutine):
  # Start the coroutine as a separate task
  task = asyncio.create_task(coroutine)

  # Tick the event loop until the task finishes, recording the longest gap between ticks
  max_gap = 0.0
  last_tick = time.monotonic()
  while not task.done():
    await asyncio.sleep(0.01)
    now = time.monotonic()
    max_gap = max(max_gap, now - last_tick)
    last_tick = now

  # Raise any error from the task, then return the longest gap
  await task
  return max_gap

# DATASET LOCATION FIXTURES
# Writes each test's datasets to its own temporary save location, so tests never write to ~/torchsig_datasets
@pytest.fixture(autouse=True)
def affixed_dataset_location(tmp_path, monkeypatch):
  location = tmp_path / 'torchsig_datasets'
  monkeypatch.setenv('TORCHSIGGUI_DATASET_LOCATION', str(location))
  yield location

# CLIENT FIXTURES
# Affixes a test client object for creating API calls
@pytest.fixture
def affixed_client():
  # Create a server application instance
  app = create_app()

  # Start a test client that listens to the server and return the running test client
  # - Uses localhost, since the server rejects requests addressed to other host names
  with TestClient(app, base_url='http://localhost') as client:
    yield client

# DATASET FIXTURES
# Affixes a file id for a generated dataset file
@pytest_asyncio.fixture
async def affixed_test_dataset_file(affixed_client):
  # Generate the dataset file and get its id
  test_file_id = await generate_test_dataset_file(TEST_DATA / 'data_default.json')

  # Return the test file id
  yield test_file_id

# Affixes a file id for a generated dataset file
@pytest_asyncio.fixture
async def affixed_test_spectrogram_dataset_file(affixed_client):
  # Generate the dataset file and get its id
  test_file_id = await generate_test_dataset_file(TEST_DATA / 'data_spectrogram.json')

  # Return the test file id
  yield test_file_id