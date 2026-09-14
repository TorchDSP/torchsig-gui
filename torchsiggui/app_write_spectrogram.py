import matplotlib.pyplot as plt
import numpy as np

from torchsiggui.files.file_io import DATASET_FOLDER
from torchsiggui.files.database_io import (
  generate_spectrogram_filename,
  run_query,
  queries
)
from torchsiggui.utils.torchsig_interface import torchsig_custom_dataset

# Writes a dataset generator from user input
async def _build_dataset(data_json):
  # Get the form data
  metadata_json = data_json['metadata']
  generation_json = data_json['generation']
  transforms_json = data_json['transforms']
  seed = data_json['seed'] if 'seed' in data_json else None

  # Build the dataset
  dataset = torchsig_custom_dataset(metadata_json, generation_json, transforms_json, seed)

  # Test the dataset by attempting to create a sample signal
  _test_sample = next(dataset)

  # Return the built dataset generator
  return dataset

# Generates an image for a signal generated from user input
async def create_sample_image(data_json) -> None:
  # Generate a new file name
  image_name = await generate_spectrogram_filename()

  try:
    # Create the dataset and get a sample from it
    dataset = await _build_dataset(data_json)
    sample = next(dataset)
    data = sample.data

    # Set the sample rate for the spectrogram
    t = np.arange(0, len(data)) / dataset.sample_rate

    # Plot the spectrogram image
    fig = plt.figure(figsize=(12, 4))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(t, np.real(data), alpha=0.5, label='Real')
    ax.plot(t, np.imag(data), alpha=0.5, label='Imag')
    ax.set_xlim([t[0], t[-1]])
    ax.set_xlabel('Time (sec)')
    ax.set_ylabel('Amplitude')
    ax.grid()

    # Save the image, and close the plotter
    plt.savefig(DATASET_FOLDER / image_name)
    plt.close()

    # Update the stored filename to match the image saved
    await run_query(queries.update_complete_spectrogram)

  # If image creation fails, print an error to the server console
  except Exception as error:
    print('An error occured while trying to create a new spectrogram image: ' + str(error))