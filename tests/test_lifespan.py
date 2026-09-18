# LIFESPAN TESTS
# Tests the startup and shutdown procedures of the FastAPI server

import pytest
from fastapi.testclient import TestClient

from shutil import rmtree
from unittest.mock import patch

from torchsiggui.main import create_app
from torchsiggui.files.file_io import SESSION_FOLDER, DATABASE
from torchsiggui.files.database_io import run_query, queries, get_file_info

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

@pytest.mark.asyncio
async def test_lifespan_clears_records_left_by_previous_session():
  try:
    # Start a server and leave a file entry and an unfinished spectrogram in the database
    # - Skips deleting the session folder on shutdown, as happens on Windows when another program has the database open
    with patch('torchsiggui.main.rmtree'):
      with TestClient(create_app()):
        await run_query(queries.add_file_entry, file_id='stale_id', total=10, filepath='/datasets/stale')
        await run_query(queries.update_start_spectrogram, new_name='stale.png')
    assert DATABASE.exists()

    # The next server should start with no file entries and no unfinished spectrogram
    with TestClient(create_app()):
      assert await get_file_info() == {}
      assert await run_query(queries.get_spectrogram_details) == { 'current_name': '', 'complete': 1 }
  finally:
    # Remove the dataset folder and database in case they still exist after the test concludes
    if SESSION_FOLDER.exists():
      rmtree(SESSION_FOLDER)
