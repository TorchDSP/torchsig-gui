import asyncio
import concurrent.futures
import threading

from pathlib import Path
from typing import Any

from torchsiggui.files.database_io import (
  generate_file_entry,
  run_query,
  queries
)
from torchsiggui.files.file_io import (
  DATASET_FOLDER,
  ARCHIVE_EXTENSION,
  create_archive_file
)
from torchsiggui.utils.torchsig_interface import (
  torchsig_custom_dataset,
  torchsig_custom_dataloader,
  update_dataset_yaml,
  update_writer_yaml
)

# Characters that are not allowed in Windows file names, plus control characters
INVALID_NAME_CHARACTERS = set('<>:"/\\|?*') | {chr(code) for code in range(32)}

# Device names that Windows reserves in every folder, with or without an extension
RESERVED_NAMES = {'CON', 'PRN', 'AUX', 'NUL'} | {f'{device}{n}' for device in ('COM', 'LPT') for n in range(1, 10)}

# Checks that a dataset name is a plain folder name that is valid on Windows, macOS, and Linux
# - Rejects path separators and '..', so the name cannot write outside the dataset folder
# - Applies the Windows naming rules on every platform, so a name that works on one server works on all of them
def validate_dataset_name(name) -> None:
  if (
    not isinstance(name, str)
    or name in ('', '.', '..')
    or Path(name).name != name
    or any(char in INVALID_NAME_CHARACTERS for char in name)
    or name[-1] in '. '
    or name.split('.')[0].upper() in RESERVED_NAMES
  ):
    raise ValueError(f'Invalid dataset name: {name!r}')

# Tracks a new file and returns its id
#   Raises ValueError for an invalid name and DuplicateFileError if the name is already in use
async def track_new_file(data_json):
  # Get the filename and total length from the form data
  filename = data_json['dataset']['root']
  total_batches = data_json['dataset']['length']

  # Reject names that could write outside the dataset folder
  validate_dataset_name(filename)

  # Generate a new file entry for this file and keep the file id
  new_file_id = await generate_file_entry(total_batches, filename + '.' + ARCHIVE_EXTENSION)

  # Update the data json root to be absolute for future processing
  data_json['dataset']['root'] = DATASET_FOLDER / new_file_id / filename

  # Return the file id
  return new_file_id

# Writes a dataset file creator from user input
def _build_dataset_creator(data_json, file_id, run_query_sync):
  # Get the form data
  run_query_sync(queries.update_current_status, file_id=file_id, new_status='Parsing Data...')
  metadata_json = data_json['metadata']
  generation_json = data_json['generation']
  transforms_json = data_json['transforms']
  dataset_json = data_json['dataset']
  seed = data_json['seed'] if 'seed' in data_json else None

  # Build the dataset
  run_query_sync(queries.update_current_status, file_id=file_id, new_status='Building Signal Generators...')
  dataset = torchsig_custom_dataset(metadata_json, generation_json, transforms_json, seed)

  # Test the dataset by attempting to create a sample signal
  run_query_sync(queries.update_current_status, file_id=file_id, new_status='Testing Signal Generation...')
  _test_sample = next(dataset)

  # Assemble the dataset creator
  run_query_sync(queries.update_current_status, file_id=file_id, new_status='Building Dataset Creator...')
  creator = torchsig_custom_dataloader(dataset, dataset_json)

  # Return the built dataset creator
  return creator

# Writes the dataset file and its archive from user input
#   Runs in a worker thread, so the slow TorchSig and file work does not block the server
#   Uses run_query_sync to run database queries on the server's event loop
def _write_dataset_file(data_json, file_id, run_query_sync) -> None:
  # Create the dataset creator from user input
  dataset_creator = _build_dataset_creator(data_json, file_id, run_query_sync)

  # Use the dataset creator to create the dataset file
  run_query_sync(queries.update_current_status, file_id=file_id, new_status='Creating Dataset Files...')
  dataset_creator.items_written = 0
  with dataset_creator.file_handler(root=dataset_creator.root) as writer:
    # Write initial YAMLs
    update_dataset_yaml(dataset_creator)
    update_writer_yaml(dataset_creator, complete=False)

    # Track the number of items that remain to be written
    remaining = dataset_creator.dataset_length_requested

    # Run this loop if multithreading is desired
    if dataset_creator.multithreading:
      # Set a writing lock and a list of writing threads
      writer_lock = threading.Lock()
      futures: list[concurrent.futures.Future[int]] = []

      # Define the function that a writing thread should run to write to the dataset file
      #   Waits until it holds the lock, then writes and releases the lock
      #   Returns the length of the batch written or 1 if the length cannot be found
      def submit_write(batch_idx: int, batch: Any) -> int:
        with writer_lock:
          writer.write(batch_idx, batch)
        return len(batch) if hasattr(batch, "__len__") else 1

      # Loops through each batch via index using a pool of writing threads
      # Single executor; max_workers=1 is enough since writer calls are serialized
      batch_idx = 0
      with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        # Loop through all of the batches requested
        for batch in dataset_creator.dataloader:
          # If there are no batches left to read into the dataset file or the file has been cancelled, break the loop
          if remaining <= 0 or run_query_sync(queries.get_is_cancelled, file_id=file_id):
            break

          # Get the next batch and the batch length
          if hasattr(batch, "__len__") and len(batch) > remaining:
            batch = batch[:remaining]
          batch_len = len(batch) if hasattr(batch, "__len__") else 1

          # Use a thread to write to the dataset file
          futures.append(executor.submit(submit_write, batch_idx, batch))

          # Update the batch index and the remaining batches left to read
          batch_idx += 1
          remaining -= batch_len

          # Wait until all threads finish before starting the next wave of writes
          if len(futures) >= dataset_creator.max_inflight_futures:
            for fut in futures:
              # Update the items written and the progress for the file info mapping
              dataset_creator.items_written += fut.result()
              run_query_sync(queries.update_file_progress, file_id=file_id)
            futures.clear()

        # Loop through all of the batches that remain to be written to the dataset file
        for fut in futures:
          # Update the items written and the progress for the file info mapping
          dataset_creator.items_written += fut.result()
          run_query_sync(queries.update_file_progress, file_id=file_id)

    # Run this loop if multithreading is not desired
    else:
      # Loop through each batch via index using a single, non-threaded writer
      batch_idx = 0
      for batch in dataset_creator.dataloader:
        # If there are no batches left to read into the dataset file or the file has been cancelled, break the loop
        if remaining <= 0 or run_query_sync(queries.get_is_cancelled, file_id=file_id):
          break

        # Get the next batch and the batch length
        if hasattr(batch, "__len__") and len(batch) > remaining:
          batch = batch[:remaining]
        batch_len = len(batch) if hasattr(batch, "__len__") else 1

        # Use the non-threaded writer to write to the dataset file
        writer.write(batch_idx, batch)

        # Update the batch index and the remaining batches left to read
        batch_idx += 1
        remaining -= batch_len

        # Update the items written and the progress for the file info mapping
        dataset_creator.items_written += batch_len
        run_query_sync(queries.update_file_progress, file_id=file_id)

  # Write final YAMLs
  run_query_sync(queries.update_current_status, file_id=file_id, new_status='Assembling Archive File...')
  update_dataset_yaml(dataset_creator)
  update_writer_yaml(dataset_creator, complete=True)

  # Create an archive file containing all dataset resources
  create_archive_file(dataset_creator.root.name, dataset_creator.root.parent)

  # Validate that all signals have been written to the dataset
  complete_status = 'Complete'
  if dataset_creator.items_written != dataset_creator.dataset_length_requested:
    complete_status += f"; DatasetCreator wrote {dataset_creator.items_written} samples, expected {dataset_creator.dataset_length_requested}"

  # Once the dataset file write has finished, mark the file as complete
  run_query_sync(queries.complete_file, file_id=file_id, complete_status=complete_status)

# Creates a dataset file from user input
#   Uses the file id from track_new_file if given, otherwise starts tracking the file here
async def create_dataset_file(data_json, file_id: str | None = None) -> None:
  # Start tracking the development of the new dataset file
  if file_id is None:
    file_id = await track_new_file(data_json)

  # Define a function that lets the worker thread run database queries on this event loop and wait for the result
  loop = asyncio.get_running_loop()
  def run_query_sync(sql_query, **kwargs):
    return asyncio.run_coroutine_threadsafe(run_query(sql_query, **kwargs), loop).result()

  # Attempt to write the requested signals to the dataset file in a worker thread
  try:
    await asyncio.to_thread(_write_dataset_file, data_json, file_id, run_query_sync)

  # If the write fails, mark the file as complete but not ready, with the error as its status for the user to see
  # - Marking it complete lets a later cancel request clean up the partial files
  except Exception as error:
    await run_query(queries.fail_file, file_id=file_id, error_status=str(error))