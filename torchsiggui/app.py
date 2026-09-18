import torchsiggui.app_lookup as app_lookup
from torchsiggui.app_write_dataset import create_dataset_file, track_new_file, read_dataset_complete
from torchsiggui.app_write_spectrogram import create_sample_image

from torchsiggui.files.file_io import SESSION_FOLDER
from torchsiggui.files.database_io import (
  run_query,
  queries,
  get_file_info,
  DuplicateFileError
)

import logging

from asyncio import sleep, create_task, to_thread
from pathlib import Path
from shutil import rmtree

from fastapi import (
  APIRouter,
  BackgroundTasks,
  WebSocket,
  WebSocketDisconnect,
  HTTPException
)

# Creates a router to store the server routes
router = APIRouter()

# Creates a logger for files that could not be deleted
logger = logging.getLogger(__name__)

# Deletes a file, logging instead of failing if it cannot be removed
# - Windows cannot delete a file while it is open, such as an image that is still being sent to a browser
# - Any file left behind is removed with the session folder when the server shuts down
def remove_file(file_path: Path) -> None:
  try:
    file_path.unlink(missing_ok=True)
  except OSError as error:
    logger.warning('Could not delete %s: %s', file_path, error)

# FASTAPI REQUEST HANDLERS
# Connects requests from the client to API functions and returns the results

@router.get('/api/metadata-defaults')
def get_metadata_defaults():
  # Return the TorchSig metadata defaults
  return app_lookup.lookup_metadata_defaults()

@router.get('/api/generator-options')
def get_generator_options():
  # Return the TorchSig signal generator options
  return app_lookup.lookup_generator_options()

@router.get('/api/transform-options')
def get_transform_options():
  # Return the TorchSig signal transform options
  return app_lookup.lookup_transform_options()

@router.get('/api/dataset-defaults')
def get_dataset_defaults():
  # Return the TorchSig dataset defaults
  return app_lookup.lookup_dataset_defaults()

# FASTAPI WRITE HANDLERS
# Connects write requests from the client to API functions and launches background write tasks

# FastAPI rejects request bodies that are not JSON objects with a 422 response before these handlers run

@router.post('/api/write-sample')
def post_write_sample(data_json: dict, background_tasks: BackgroundTasks):
  # Start generating the signal sample
  background_tasks.add_task(create_sample_image, data_json)

  # Return a success message
  return { 'message': 'success' }

@router.post('/api/write-dataset')
async def post_write_dataset(data_json: dict, background_tasks: BackgroundTasks):
  # Start tracking the new dataset before responding, so name and save location problems are reported to the user
  try:
    file_id = await track_new_file(data_json)
  except DuplicateFileError as error:
    raise HTTPException(status_code=409, detail=str(error))
  except KeyError as error:
    raise HTTPException(status_code=400, detail=f'Missing dataset field: {error}')
  except (TypeError, ValueError) as error:
    raise HTTPException(status_code=400, detail=str(error))

  # Start building the dataset creator and creating the dataset file
  background_tasks.add_task(create_dataset_file, data_json, file_id)

  # Return a success message
  return { 'message': 'success' }

# FASTAPI DATASET HANDLERS
# Connects dataset list requests from the client to API functions

@router.delete('/api/cancel-dataset/{file_id}')
async def delete_cancel_dataset(file_id: str):
  # Get the file_info map and check for the file
  file_info = await get_file_info()

  # Raise an exception if the file does not exist
  if file_id not in file_info:
    raise HTTPException(status_code=404, detail='File not found')

  # If the dataset finished writing, only remove it from the list, keeping its files where the user saved them
  if file_info[file_id]['ready']:
    await run_query(queries.delete_file_entry, file_id=file_id)
    return { 'message': 'success' }

  # Otherwise, mark the dataset as cancelled
  await run_query(queries.cancel_file, file_id=file_id)

  # Wait for the background task to complete
  while True:
    is_logged = file_id in await get_file_info()
    if not is_logged:
      break
    is_complete = await run_query(queries.get_is_complete, file_id=file_id)
    if is_complete:
      break

    # Return control to the FastAPI event loop so the background task can finish
    await sleep(0.1)

  # Remove the dataset from the list
  await run_query(queries.delete_file_entry, file_id=file_id)

  # Delete the partial dataset folder, in a worker thread since large datasets can take a while to remove
  # - Keeps the folder if it still holds a finished dataset, such as one that was going to be overwritten
  #   but was not replaced because the new dataset failed or was cancelled before writing started
  folder_path = Path(file_info[file_id]['filepath'])
  if folder_path.is_dir() and not folder_path.is_symlink() and not read_dataset_complete(folder_path):
    await to_thread(rmtree, folder_path, ignore_errors=True)

  # Return a success message
  return { 'message': 'success' }

# FASTAPI WEBSOCKET
# Creates a websocket to stream file and spectrogram info changes to the webpage

@router.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
  # Start the stream loop when the client connects to the websocket
  await websocket.accept()

  # Define the task to check for changes in the spectrogram info map and send updates to the client
  async def sample_info_feed():
    # Create a variable to store the previous spectrogram info map for update detection
    last_image = dict()
    while True:
      # Get the spectrogram info map
      this_image = await run_query(queries.get_spectrogram_details)

      # If the map has changed, send the updated filename to the client, delete the old file, and update the map to check against
      if this_image != last_image and this_image['current_name'] and this_image['complete']:
        await websocket.send_json({ 'type': 'spectrogram', 'update': this_image['current_name'] })
        if 'current_name' in last_image:
          remove_file(SESSION_FOLDER / last_image['current_name'])
        last_image = this_image

      # Return control to the FastAPI event loop to process other requests between checks
      await sleep(0.1)

  # Define the task to check for changes in the file info map and send updates to the client
  async def file_info_feed():
    # Create a variable to store the previous file info map for update detection
    last_map = dict()
    while True:
      # Get the file info map
      this_map = await get_file_info()

      # If the map has changed, send the updated map to the client and update the map to check against
      if this_map != last_map:
        await websocket.send_json({ 'type': 'file', 'update': this_map })
        last_map = this_map

      # Return control to the FastAPI event loop to process other requests between checks
      await sleep(0.1)

  # Start the feed tasks
  sample_task = create_task(sample_info_feed())
  file_task = create_task(file_info_feed())

  # Constantly check for messages from the client
  try:
    while True:
      await websocket.receive_text()

  # Exit the loop when the client disconnects
  except WebSocketDisconnect:
    pass

  # Stop the feed tasks however the connection ends
  finally:
    sample_task.cancel()
    file_task.cancel()