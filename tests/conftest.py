# PYTEST CONFTEST FILE
# Defines fixtures for common code chunks used in other tests

from fastapi.testclient import TestClient

import json
import pytest
import pytest_asyncio
from pathlib import Path

from torchsiggui.main import create_app
from torchsiggui.app_write_dataset import create_dataset_file
from torchsiggui.files.database_io import get_file_info

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

# CLIENT FIXTURES
# Affixes a test client object for creating API calls
@pytest.fixture
def affixed_client():
  # Create a server application instance
  app = create_app()

  # Start a test client that listens to the server and return the running test client
  with TestClient(app) as client:
    yield client

# DATASET FIXTURES
# Affixes a file id for a generated dataset file
@pytest_asyncio.fixture
async def affixed_test_dataset_file(affixed_client):
  # Generate the dataset file and get its id
  test_file_id = generate_test_dataset_file(TEST_DATA / 'data_default.json')

  # Return the test file id
  yield test_file_id

# Affixes a file id for a generated dataset file
@pytest_asyncio.fixture
async def affixed_test_spectrogram_dataset_file(affixed_client):
  # Generate the dataset file and get its id
  test_file_id = generate_test_dataset_file(TEST_DATA / 'data_spectrogram.json')

  # Return the test file id
  yield test_file_id