# LIFESPAN TESTS
# Tests the startup and shutdown procedures of the FastAPI server

from fastapi.testclient import TestClient

from shutil import rmtree

from torchsiggui.main import create_app
from torchsiggui.files.file_io import SESSION_FOLDER, DATABASE

def test_lifespan():
  try:
    # The dataset folder and database should not exist before the server has started
    assert not SESSION_FOLDER.exists()

    # Start running the server
    app = create_app()
    with TestClient(app):
      # The dataset folder and database should exist when the server is running
      assert SESSION_FOLDER.is_dir()
      assert (DATABASE).exists()

    # The dataset folder and database should not exist after the server has shut down
    assert not SESSION_FOLDER.exists()
  finally:
    # Remove the dataset folder and database in case they still exist after the test concludes
    if SESSION_FOLDER.exists():
      rmtree(SESSION_FOLDER)