import sys

from os import environ, walk
from pathlib import Path
from zipfile import ZipFile, ZIP_STORED

# DIRECTORY LOCATIONS
# Creates variables to store the main application folders
MODULE_FOLDER = Path(__file__).resolve().parent.parent
QUERY_FILE = MODULE_FOLDER / 'files' / 'database_sql.sql'
WEBBUILD_FOLDER = MODULE_FOLDER / 'webbuild'

# Returns the usual folder for application cache data on this operating system
# - Windows: %LOCALAPPDATA%
# - macOS: ~/Library/Caches
# - Linux: $XDG_CACHE_HOME, or ~/.cache
def get_cache_folder() -> Path:
  if sys.platform == 'win32':
    return Path(environ.get('LOCALAPPDATA') or Path.home() / 'AppData' / 'Local')
  if sys.platform == 'darwin':
    return Path.home() / 'Library' / 'Caches'
  return Path(environ.get('XDG_CACHE_HOME') or Path.home() / '.cache')

# Creates variables to store the external folders and files
# - Uses TORCHSIGGUI_DATA_DIR if set, otherwise the user cache folder, so data is never written into the install location
DATA_FOLDER = Path(environ.get('TORCHSIGGUI_DATA_DIR') or get_cache_folder() / 'torchsiggui')
DATASET_FOLDER = DATA_FOLDER / 'datasets'
DATABASE = DATASET_FOLDER / 'state.db'

# ARCHIVE FUNCTIONS
# Datasets are always downloaded as zip files, since every operating system can open them without extra tools
ARCHIVE_EXTENSION = 'zip'

# Creates an archive file in the dataset folder containing everything inside a folder
# - Stores files without compression, since dataset files barely compress and compressing large datasets is slow
def create_archive_file(filename: str, to_zip: Path):
  with ZipFile(DATASET_FOLDER / (filename + '.' + ARCHIVE_EXTENSION), 'w', ZIP_STORED) as archive:
    for folder, folder_names, file_names in walk(to_zip):
      folder_names.sort()
      for name in folder_names + sorted(file_names):
        path = Path(folder) / name
        archive.write(path, path.relative_to(to_zip))

# Extracts archive files
def extract_archive_file(filename: Path, dest: Path):
  with ZipFile(filename) as archive:
    archive.extractall(dest)
