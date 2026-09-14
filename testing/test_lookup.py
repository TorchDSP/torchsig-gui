# LOOKUP PROCEDURE TESTS
# Tests the lookup procedures for retrieving TorchSig data structures

from torchsig.utils.defaults import TorchSigDefaults

from torchsiggui.utils.torchsig_interface import (
  torchsig_transform_map,
  torchsig_generators_by_family,
  torchsig_dummy_creator
)

def test_get_metadata_defaults(affixed_client):
  # Get the metadata defaults from the server
  response = affixed_client.get('/api/metadata-defaults')

  # The correct metadata defaults should be returned
  assert response.status_code == 200
  assert response.json() == TorchSigDefaults().default_dataset_metadata

def test_get_generator_options(affixed_client, subtests):
  # Get the signal generator options from the server
  response = affixed_client.get('/api/generator-options')

  # The correct status code should be returned
  assert response.status_code == 200

  # Get the response generator options and actual generator options
  generator_options = response.json()
  torchsig_generator_options = torchsig_generators_by_family()

  # The response generator options should have the correct families and all families within the 'families' family
  assert set(generator_options.keys()) == set(torchsig_generator_options.keys()) | { 'families' }
  assert set(generator_options['families']) == set(torchsig_generator_options.keys()) | { 'all' }

  # The response generator options should have the correct generator options within each family
  for family in torchsig_generator_options.keys():
    with subtests.test(msg='Generator Test', family=family):
      assert generator_options[family] == torchsig_generator_options[family]

def test_get_transform_options(affixed_client):
  # Get the signal transform options from the server
  response = affixed_client.get('/api/transform-options')

  # The correct transform options should be returned
  assert response.status_code == 200

  transform_options = response.json()
  assert torchsig_transform_map().keys() == transform_options.keys()

def test_get_dataset_defaults(affixed_client):
  # Get the dataset defaults from the server
  response = affixed_client.get('/api/dataset-defaults')

  # The correct dataset defaults should be returned
  assert response.status_code == 200

  default_creator = torchsig_dummy_creator()
  dataset_defaults = response.json()
  assert default_creator.overwrite == dataset_defaults['overwrite']
  assert default_creator.multithreading == dataset_defaults['multithreading']