import aiosql
import aiosqlite
from contextlib import asynccontextmanager
from nanoid import generate

from torchsiggui.files.file_io import DATABASE, QUERY_FILE

# Creates an object to reference database queries
queries = aiosql.from_path(QUERY_FILE, 'aiosqlite')

# Raised when a new file entry uses a file path that is already in use
class DuplicateFileError(ValueError):
  pass

# Wraps handlers for opening database connections
@asynccontextmanager
async def get_db():
  # Create a database connection with a timeout of 5 seconds
  db = await aiosqlite.connect(DATABASE, timeout=5.0)

  # Change the generated rows to behave like dictionaries
  db.row_factory = aiosqlite.Row

  # Change the connection to use write-ahead logging mode with a timeout of 5 seconds
  await db.execute('PRAGMA journal_mode=WAL')
  await db.execute('PRAGMA busy_timeout=5000')

  # Yield the database connection, closing it when done even if a query fails
  try:
    yield db
  finally:
    await db.close()

# Runs a query and returns the parsed result
async def run_query(sql_query, **kwargs):
  async with get_db() as db:
    try:
      # Get the result of a query, an async object
      raw_result = await sql_query(db, **kwargs)

      # Commit the changes to the database
      await db.commit()

      # Parse the results for single rows and single values
      if 'row' in str(type(raw_result)).lower():
        result = dict(raw_result)
      else:
        result = raw_result

      # Return the parsed results
      return result
    except Exception:
      # Rollback the change and raise an exception if something goes wrong
      await db.rollback()
      raise

# Runs the worker info query and returns the parsed result
async def get_worker_info():
  async with get_db() as db:
    try:
      # Get the result of the query, an async generator
      async_gen = queries.get_worker_info(db)

      # Extract everything from the async generator
      result = list()
      async for row_item in async_gen:
        result.append(dict(row_item))

      # Commit the changes to the database
      await db.commit()

      # Return the parsed results
      return result
    except Exception:
      # Rollback the change and raise an exception if something goes wrong
      await db.rollback()
      raise

# Runs the file info query and returns the parsed result
async def get_file_info():
  async with get_db() as db:
    try:
      # Get the result of the query, an async generator
      async_gen = queries.get_file_info(db)

      # Extract everything from the async generator
      raw_result = list()
      async for row_item in async_gen:
        raw_result.append(dict(row_item))

      # Commit the changes to the database
      await db.commit()

      # Parse the multi-row results
      result = dict()
      for row in raw_result:
        file_id = row.pop('id')
        row['complete'] = bool(row['complete'])
        row['ready'] = bool(row['ready'])
        result[file_id] = row

      # Return the parsed results
      return result
    except Exception:
      # Rollback the change and raise an exception if something goes wrong
      await db.rollback()
      raise

# Generates a new entry to the file table
async def generate_file_entry(total: int, filepath: str):
  while True:
    # Try to add a new row to the file table and return the succeeding file id
    try:
      file_id = generate()
      await run_query(queries.add_file_entry, file_id=file_id, total=total, filepath=filepath)
      return file_id
    # If the file id collides, try again; if the file path is already in use, stop
    except aiosqlite.IntegrityError as error:
      if 'filepath' in str(error):
        raise DuplicateFileError(
          f"A dataset at '{filepath}' already exists in the dataset list. Remove it from the list, or choose a different name."
        ) from error
      continue

# Generates a new spectrogram filename
async def generate_spectrogram_filename():
  while True:
    # Try to add a new row to the spectrogram table and return the succeeding image name
    try:
      image_id = generate()
      image_name = image_id + '.png'
      await run_query(queries.update_start_spectrogram, new_name=image_name)
      return image_name
    # If the row add fails, try again
    except aiosqlite.IntegrityError:
      continue