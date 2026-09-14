from pathlib import Path
from platform import system
from shutil import make_archive, unpack_archive

# DIRECTORY LOCATIONS
# Creates variables to store the main application folders
MODULE_FOLDER = Path(__file__).resolve().parent.parent
QUERY_FILE = MODULE_FOLDER / 'files' / 'database_sql.sql'
WEBBUILD_FOLDER = MODULE_FOLDER / 'webbuild'

# Creates variables to store the external folders and files
MODULE_PARENT_FOLDER = MODULE_FOLDER.parent
MODULE_LOCK_FILE = MODULE_PARENT_FOLDER / 'workers.lock'
DATASET_FOLDER = MODULE_PARENT_FOLDER / 'datasets'
DATABASE = DATASET_FOLDER / 'state.db'

# ARCHIVE FUNCTIONS
# Determines the archive file extension
def get_archive_extension():
  return 'zip' if system() == 'Windows' else 'tar'

# Creates archive files
def create_archive_file(filename: str, to_zip: Path):
  make_archive((DATASET_FOLDER / filename), get_archive_extension(), root_dir=to_zip)

# Extracts archive files
def extract_archive_file(filename: str, dest: Path):
  if get_archive_extension() == 'zip':
    unpack_archive(filename, extract_dir=dest)
  else:
    unpack_archive(filename, extract_dir=dest, format='tar', filter='data')