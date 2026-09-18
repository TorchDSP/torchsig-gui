from torchsiggui.files.file_io import SERVER_HOSTNAME, get_default_dataset_location
from torchsiggui.utils.inspection import get_class_parameters
from torchsiggui.utils.torchsig_interface import (
  torchsig_transform_map,
  torchsig_metadata_defaults,
  torchsig_generators_by_family,
  torchsig_dummy_creator
)

# Looks up the metadata defaults
def lookup_metadata_defaults():
  # Return the TorchSig metadata defaults
  return torchsig_metadata_defaults()

# Looks up the generator options
def lookup_generator_options():
  # Start the TorchSig generator options dictionary
  generator_options = { 'families': ['all'] }

  # Add each TorchSig generator family to the dictionary
  for family, generators in torchsig_generators_by_family().items():
    generator_options[family] = generators
    generator_options['families'] += [family]

  # Return the TorchSig signal generator options
  return generator_options

# Looks up the transform options
def lookup_transform_options():
  # Create a new object to store all of the transform data in
  transform_options = dict()

  # Get all transforms from the transforms module
  for name, obj in torchsig_transform_map().items():
    # Get the next set of parameters
    transform_parameters = get_class_parameters(obj)

    # Replace all transform class parameters with a standardized type and value
    transform_class_parameters = [name for name in transform_parameters.keys() if 'transform' in name]
    for name in transform_class_parameters:
      del transform_parameters[name]
      transform_parameters['transforms'] = { 'type': 'transforms', 'value': [] }

    # Add the next set of parameters to the transform options
    transform_options[name] = transform_parameters

  # Return the TorchSig signal transform options
  return transform_options

# Looks up the dataset defaults
def lookup_dataset_defaults():
  # Create a dummy dataset creator
  default_creator = torchsig_dummy_creator()

  # Get the dataset defaults
  # - Overwrite is off by default, since datasets are kept in the save location and overwriting replaces one
  # - The hostname tells the user which machine the save location is on
  dataset_defaults = {
    'overwrite': False,
    'multithreading': default_creator.multithreading,
    'location': str(get_default_dataset_location()),
    'hostname': SERVER_HOSTNAME
  }

  # Return the TorchSig dataset defaults
  return dataset_defaults