# MAIN TESTS
# Tests the command arguments and configuration used to start the server

import pytest
import sys
from os import environ
from unittest.mock import patch

from torchsiggui.main import AppConfig, apply_args_to_environment, create_app, main, parse_args

# Clears the server settings from the environment for each test, restoring them afterwards
@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
  monkeypatch.delenv('TORCHSIGGUI_PORT', raising=False)
  monkeypatch.delenv('TORCHSIGGUI_DEV_MODE', raising=False)

def test_parse_args_defaults():
  # No arguments should leave every setting unset
  args = parse_args([])
  assert args.port is None
  assert args.dev is False

def test_parse_args_values():
  # The port and development flags should be parsed
  args = parse_args(['--port', '9000', '--dev'])
  assert args.port == 9000
  assert args.dev is True

def test_parse_args_invalid():
  # Unknown arguments and invalid ports should exit with a usage message
  with pytest.raises(SystemExit):
    parse_args(['--unknown'])
  with pytest.raises(SystemExit):
    parse_args(['--port', 'not_a_port'])

def test_apply_args_to_environment():
  # Command arguments should become the server configuration
  apply_args_to_environment(parse_args(['-p', '9000', '--dev']))
  assert environ['TORCHSIGGUI_PORT'] == '9000'

  config = AppConfig()
  assert config.port == 9000
  assert config.dev_mode is True

def test_apply_args_to_environment_defaults():
  # No command arguments should keep the default configuration
  apply_args_to_environment(parse_args([]))

  config = AppConfig()
  assert config.port == 8000
  assert config.dev_mode is False

def test_create_app_ignores_command_arguments(monkeypatch):
  # Creating the app should not parse the arguments of the process hosting it
  monkeypatch.setattr(sys, 'argv', ['pytest', '-p', 'no:cacheprovider'])
  assert create_app() is not None

def test_main_starts_server():
  # The server should start on the requested port without reloading
  with patch('torchsiggui.main.uvicorn.run') as mock_run:
    main(['--port', '9001'])
  mock_run.assert_called_once_with('torchsiggui.main:create_app', factory=True, host='127.0.0.1', port=9001, reload=False)

def test_main_starts_dev_server():
  # The development server should reload on code changes
  with patch('torchsiggui.main.uvicorn.run') as mock_run:
    main(['--dev'])
  mock_run.assert_called_once_with('torchsiggui.main:create_app', factory=True, host='127.0.0.1', port=8000, reload=True)
