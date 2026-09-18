# DATASET TESTS
# Tests that the contents of dataset files are readable and contain the correct data

import numpy as np
import pytest

from torchsig.utils.file_handlers.hdf5 import HDF5Reader

from torchsiggui.files.file_io import DATASET_FOLDER
from torchsiggui.files.database_io import get_file_info

@pytest.mark.asyncio
async def test_dataset_non_spectrogram(affixed_test_dataset_file):
  # Define the file id for the dataset file
  test_file_id = affixed_test_dataset_file

  # Get the dataset file directory by the id
  file_info = await get_file_info()
  test_filepath = file_info[test_file_id]['filepath']
  test_folder = test_filepath[:test_filepath.rfind('.')]

  # Get a signal from the dataset file
  reader = HDF5Reader(DATASET_FOLDER / test_file_id / test_folder)
  signal = reader.read(0)
  reader.teardown()

  # The signal should not be a spectrogram
  data = signal.data
  assert isinstance(data, np.ndarray)
  assert data.ndim != 2

@pytest.mark.asyncio
async def test_dataset_spectrogram(affixed_test_spectrogram_dataset_file):
  # Define the file id for the dataset file
  test_file_id = affixed_test_spectrogram_dataset_file

  # Get the dataset file directory by the id
  file_info = await get_file_info()
  test_filepath = file_info[test_file_id]['filepath']
  test_folder = test_filepath[:test_filepath.rfind('.')]

  # Get a signal from the dataset file
  reader = HDF5Reader(DATASET_FOLDER / test_file_id / test_folder)
  signal = reader.read(0)
  reader.teardown()

  # The signal should be a spectrogram
  data = signal.data
  assert isinstance(data, np.ndarray)
  assert data.ndim == 2
  assert data.shape[0] == 512
  assert np.issubdtype(data.dtype, np.floating)
  assert np.all(np.isfinite(data))