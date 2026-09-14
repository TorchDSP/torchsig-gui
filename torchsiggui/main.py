from torchsiggui.app import router
from torchsiggui.files.file_io import DATASET_FOLDER, MODULE_LOCK_FILE, WEBBUILD_FOLDER
from torchsiggui.files.database_io import (
  run_query,
  queries,
  get_worker_info
)

import argparse
import psutil
import uvicorn

from contextlib import asynccontextmanager
from filelock import FileLock
from importlib.metadata import version, PackageNotFoundError
from os import makedirs, getpid
from pydantic_settings import BaseSettings, SettingsConfigDict
from shutil import rmtree

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# FASTAPI CONFIGURATION
# Handles the configuration of server application instances

# Defines a class to store the server configuration details
class AppConfig(BaseSettings):
  # Server settings
  port: int = 8000
  workers: int = 1

  # Development settings
  dev_mode: bool = False

  # Override the default configuration details with a .env file, if present
  model_config = SettingsConfigDict(env_prefix='torchsiggui_', env_file='.env')

# Gets the current version of the module
def get_version() -> str:
  try:
    return version('torchsiggui')
  except PackageNotFoundError:
    from torchsiggui import __version__
    return __version__

# Gets the configuration details from the console, .env files, and defaults if needed
def get_config():
  # Get the version number
  version = get_version()

  # Set up a parser for command arguments used to start the server
  parser = argparse.ArgumentParser(prog='TorchSigGUI', description='Start the TorchSigGUI Server')
  parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + version)
  parser.add_argument('-p', '--port', type=int, help='set the server port', metavar='P')
  # parser.add_argument('-w', '--workers', type=int, help='set the number of workers', metavar='W')
  parser.add_argument('--dev', action='store_true', help=argparse.SUPPRESS)

  # Use parse_known_args so it doesn't crash on unknown fastapi flags
  args, _ = parser.parse_known_args()

  # Map user-provided arguments to Pydantic field names, if provided
  cli_overrides = {}
  if args.port: cli_overrides['port'] = args.port
  # if args.workers: cli_overrides['workers'] = args.workers
  if args.dev: cli_overrides['dev_mode'] = args.dev

  # Determine and retrieve the configuration details, overriding with command input if present
  return AppConfig(**cli_overrides)

# FASTAPI INITIALIZATION
# Handles the creation of server application instances

# Wraps server startup and shutdown tasks for each worker
@asynccontextmanager
async def startup_shutdown(app: FastAPI):
  # STARTUP TASKS
  # Acquire a lock so that other workers do not interfere with startup for this worker
  # lock = FileLock(MODULE_LOCK_FILE, preserve_lock_file=False)
  # with lock:

  # Create the dataset folder and database if they do not exist
  makedirs(DATASET_FOLDER, exist_ok=True)
  await run_query(queries.create_database)

  # Get the current set of worker processes and remove any records of crashed workers
  worker_map = await get_worker_info()
  for worker in worker_map:
    process = psutil.Process(worker['pid'])
    if not process.is_running() or process.create_time() != worker['created']:
      run_query(queries.delete_worker_entry, process_id=worker['pid'])

  # Add a new worker record for this worker
  pid = getpid()
  created = psutil.Process(pid).create_time()
  await run_query(queries.add_worker_entry, process_id=pid, created_date=created)

  # Mount the images file for this worker so it can host images
  app.mount('/images', StaticFiles(directory=DATASET_FOLDER), name='static')

  # Yield until shutdown
  yield

  # SHUTDOWN TASKS
  # Acquire a lock so that other workers do not interfere with shutdown for this worker
  # with lock:

  # Get the current set of worker processes and remove any records of crashed workers
  worker_map = await get_worker_info()
  for worker in worker_map:
    process = psutil.Process(worker['pid'])
    if not process.is_running() or process.create_time() != worker['created']:
      run_query(queries.delete_worker_entry, process_id=worker['pid'])

  # Remove the record for this worker from the database
  pid = getpid()
  await run_query(queries.delete_worker_entry, process_id=pid)

  # If this is the last worker to shut down, also delete the database and dataset folder
  active_workers = await run_query(queries.get_worker_count)
  if active_workers == 0:
    rmtree(DATASET_FOLDER)

# Creates a configured server application instance
def create_app():
  # Load the configuration details
  config = get_config()

  # Creates the FastAPI ASGI application instance
  app = FastAPI(lifespan=startup_shutdown)

  # Add the CORS middleware
  cors_port = 3000 if config.dev_mode else config.port
  allowed_origins = ['http://localhost:' + str(cors_port), 'ws://localhost:' + str(cors_port)]
  app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
  )

  # Add the frontend to host, if not in dev mode
  if not config.dev_mode:
    app.frontend('/', directory=WEBBUILD_FOLDER)

  # Add the routes for the server to host on its API
  app.include_router(router)

  # Return the created and configured app
  return app

# MAIN FUNCTION
# Starts the TorchSigGUI server

def main():
  # Load the configuration details
  config = get_config()

  # Run the server instances in the configured mode
  if config.dev_mode:
    uvicorn.run('torchsiggui.main:create_app', factory=True, host='127.0.0.1', reload=True)
  else:
    # uvicorn.run('torchsiggui.main:create_app', factory=True, host='127.0.0.1', port=config.port, workers=config.workers)
    uvicorn.run('torchsiggui.main:create_app', factory=True, host='127.0.0.1', port=config.port)