from torchsiggui.app import router
from torchsiggui.files.file_io import DATASET_FOLDER, WEBBUILD_FOLDER
from torchsiggui.files.database_io import (
  run_query,
  queries,
  get_worker_info
)

import argparse
import psutil
import uvicorn

from contextlib import asynccontextmanager
from importlib.metadata import version, PackageNotFoundError
from os import environ, makedirs, getpid
from pydantic_settings import BaseSettings, SettingsConfigDict
from shutil import rmtree

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles

# FASTAPI CONFIGURATION
# Handles the configuration of server application instances

# Host names the server answers to
# - The server only listens on 127.0.0.1, and remote use goes through an SSH tunnel to localhost
# - Rejecting other Host headers blocks DNS rebinding, where a web page points its own domain at 127.0.0.1
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Defines a class to store the server configuration details
# - Values come from TORCHSIGGUI_* environment variables, then a .env file, then the defaults below
class AppConfig(BaseSettings):
  # Server settings
  port: int = 8000

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

# Parses the command arguments used to start the server
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
  # Set up a parser for command arguments used to start the server
  parser = argparse.ArgumentParser(prog='TorchSigGUI', description='Start the TorchSigGUI Server')
  parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + get_version())
  parser.add_argument('-p', '--port', type=int, help='set the server port', metavar='P')
  parser.add_argument('--dev', action='store_true', help=argparse.SUPPRESS)

  # Parse the arguments, exiting with a usage message if any are invalid
  return parser.parse_args(argv)

# Passes command arguments to the server through environment variables
# - The server app is created by uvicorn, in a separate process when reloading, so it reads its settings from the environment
def apply_args_to_environment(args: argparse.Namespace) -> None:
  if args.port is not None: environ['TORCHSIGGUI_PORT'] = str(args.port)
  if args.dev: environ['TORCHSIGGUI_DEV_MODE'] = 'true'

# FASTAPI INITIALIZATION
# Handles the creation of server application instances

# Removes the database records of workers that are no longer running
async def remove_crashed_workers():
  worker_map = await get_worker_info()
  for worker in worker_map:
    try:
      process = psutil.Process(worker['pid'])
      crashed = not process.is_running() or process.create_time() != worker['created']
    except psutil.NoSuchProcess:
      crashed = True
    if crashed:
      await run_query(queries.delete_worker_entry, process_id=worker['pid'])

# Wraps server startup and shutdown tasks for each worker
@asynccontextmanager
async def startup_shutdown(app: FastAPI):
  # STARTUP TASKS
  # Create the dataset folder and database if they do not exist
  makedirs(DATASET_FOLDER, exist_ok=True)
  await run_query(queries.create_database)

  # Remove any records of crashed workers
  await remove_crashed_workers()

  # Add a new worker record for this worker
  pid = getpid()
  created = psutil.Process(pid).create_time()
  await run_query(queries.add_worker_entry, process_id=pid, created_date=created)

  # Mount the images file for this worker so it can host images
  app.mount('/images', StaticFiles(directory=DATASET_FOLDER), name='static')

  # Yield until shutdown
  yield

  # SHUTDOWN TASKS
  # Remove any records of crashed workers
  await remove_crashed_workers()

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
  config = AppConfig()

  # Creates the FastAPI ASGI application instance
  app = FastAPI(lifespan=startup_shutdown)

  # Reject requests addressed to any other host name
  app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)

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

def main(argv: list[str] | None = None):
  # Apply the command arguments on top of the environment and .env configuration details
  apply_args_to_environment(parse_args(argv))
  config = AppConfig()

  # Run the server in the configured mode, reloading on code changes in development mode
  uvicorn.run('torchsiggui.main:create_app', factory=True, host='127.0.0.1', port=config.port, reload=config.dev_mode)