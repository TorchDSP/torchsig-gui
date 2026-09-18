# FILE I/O TESTS
# Tests the data folder and default dataset save locations

from pathlib import Path
from unittest.mock import patch

from torchsiggui.files.file_io import get_cache_folder, get_default_dataset_location

def test_get_cache_folder_windows(monkeypatch):
  # Windows should use the local app data folder
  monkeypatch.setenv('LOCALAPPDATA', 'C:\\Users\\test\\AppData\\Local')
  with patch('sys.platform', 'win32'):
    assert get_cache_folder() == Path('C:\\Users\\test\\AppData\\Local')

def test_get_cache_folder_macos():
  # macOS should use the user caches folder
  with patch('sys.platform', 'darwin'):
    assert get_cache_folder() == Path.home() / 'Library' / 'Caches'

def test_get_cache_folder_linux(monkeypatch):
  # Linux should use XDG_CACHE_HOME if set, otherwise ~/.cache
  with patch('sys.platform', 'linux'):
    monkeypatch.setenv('XDG_CACHE_HOME', '/test/cache')
    assert get_cache_folder() == Path('/test/cache')
    monkeypatch.delenv('XDG_CACHE_HOME')
    assert get_cache_folder() == Path.home() / '.cache'

def test_get_default_dataset_location(monkeypatch):
  # The default save location should be ~/torchsig_datasets
  monkeypatch.delenv('TORCHSIGGUI_DATASET_LOCATION')
  assert get_default_dataset_location() == Path.home() / 'torchsig_datasets'

  # TORCHSIGGUI_DATASET_LOCATION should override it
  monkeypatch.setenv('TORCHSIGGUI_DATASET_LOCATION', '/test/datasets')
  assert get_default_dataset_location() == Path('/test/datasets')
