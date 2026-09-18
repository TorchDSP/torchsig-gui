# FILE I/O TESTS
# Tests the data folder location and the dataset archive files

from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile, ZIP_STORED

from torchsiggui.files.file_io import (
  ARCHIVE_EXTENSION,
  DATASET_FOLDER,
  get_cache_folder,
  create_archive_file,
  extract_archive_file
)

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

def test_create_and_extract_archive_file(affixed_client, tmp_path):
  # Create a folder with a dataset folder and files inside it
  source = tmp_path / 'source'
  (source / 'dataset' / 'data').mkdir(parents=True)
  (source / 'dataset' / 'info.yaml').write_text('info')
  (source / 'dataset' / 'data' / 'samples.h5').write_bytes(b'samples')

  # The archive should be an uncompressed zip file with the dataset folder at its top level
  create_archive_file('dataset', source)
  archive_path = DATASET_FOLDER / ('dataset.' + ARCHIVE_EXTENSION)
  with ZipFile(archive_path) as archive:
    assert sorted(archive.namelist()) == ['dataset/', 'dataset/data/', 'dataset/data/samples.h5', 'dataset/info.yaml']
    assert all(info.compress_type == ZIP_STORED for info in archive.infolist())

  # Extracting the archive should restore the same files
  extract_archive_file(archive_path, tmp_path / 'extracted')
  assert (tmp_path / 'extracted' / 'dataset' / 'info.yaml').read_text() == 'info'
  assert (tmp_path / 'extracted' / 'dataset' / 'data' / 'samples.h5').read_bytes() == b'samples'
