import sys

from os import environ
from pathlib import Path
from socket import gethostname

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

# Creates variables to store the server's working folder and files
# - Holds the server database and spectrogram images, and is removed when the server shuts down
# - Uses TORCHSIGGUI_DATA_DIR if set, otherwise the user cache folder, so data is never written into the install location
DATA_FOLDER = Path(environ.get('TORCHSIGGUI_DATA_DIR') or get_cache_folder() / 'torchsiggui')
SESSION_FOLDER = DATA_FOLDER / 'session'
DATABASE = SESSION_FOLDER / 'state.db'

# DATASET LOCATIONS
# Names the machine the server runs on, so users know where their datasets are written
SERVER_HOSTNAME = gethostname()

# Returns the default folder that datasets are written into
# - Uses TORCHSIGGUI_DATASET_LOCATION if set, otherwise ~/torchsig_datasets
# - Datasets are kept after the server shuts down
def get_default_dataset_location() -> Path:
  return Path(environ.get('TORCHSIGGUI_DATASET_LOCATION') or Path.home() / 'torchsig_datasets').expanduser()
