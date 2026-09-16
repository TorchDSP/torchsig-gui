from torchsiggui.utils.inspection import get_classes

from functools import lru_cache

import torchsig.transforms.transforms as tstf

from torchsig.datasets.datasets import TorchSigIterableDataset
from torchsig.signals.signal_lists import TorchSigSignalLists
from torchsig.transforms.impairments import Impairments
from torchsig.transforms.base_transforms import Compose, RandomApply, RandAugment, Transform
from torchsig.utils.data_loading import WorkerSeedingDataLoader
from torchsig.utils.defaults import TorchSigDefaults
from torchsig.utils.signal_building import lookup_signal_generator_by_string
from torchsig.utils.writer import DatasetCreator, identity_collate_fn
from torchsig.utils.yaml import write_dict_to_yaml

# Returns the transform map
@lru_cache
def torchsig_transform_map():
  # Get the high-level transforms that users should have access to
  base_transform_map = { 'RandomApply': RandomApply, 'RandAugment': RandAugment }  # noqa: F841

  # Get the low-level transforms that users should have access to
  # Look for classes that are strict subclasses of SignalTransform
  raw_transform_map = get_classes(tstf)
  leaf_transform_map = { name: obj for name, obj in raw_transform_map.items() if
    issubclass(obj, tstf.SignalTransform) and obj is not tstf.SignalTransform }

  # Remove all transforms that are too complex for non-technical users
  high_complexity_list = ['ComplexTo2D', 'SpectrogramImage']
  for complex_transform in high_complexity_list:
    del leaf_transform_map[complex_transform]

  # Return the complete transform map
  # return base_transform_map | leaf_transform_map
  return leaf_transform_map

# Returns the TorchSig metadata defaults
@lru_cache
def torchsig_metadata_defaults():
  # Return the TorchSig metadata defaults
  return TorchSigDefaults().default_dataset_metadata

# Returns the TorchSig generators by family
@lru_cache
def torchsig_generators_by_family():
  # Initialize the dictionary to store the TorchSig generators in
  generators_by_family = dict()

  # Add the generator options by family
  generator_dict = TorchSigSignalLists.family_dict
  for gen, fam in generator_dict.items():
    # Add the next generator under its generator family, creating a new mapping for the family if one doesn't exist
    if fam not in generators_by_family:
      generators_by_family[fam] = []
    generators_by_family[fam].append(gen)

  # Return the TorchSig generators
  return generators_by_family

# Returns a dummy TorchSig DatasetLoader for default fetching
@lru_cache
def torchsig_dummy_creator():
  # Create a dummy dataset creator
  dummy_dataset = TorchSigIterableDataset(metadata=TorchSigDefaults().default_dataset_metadata)
  dummy_loader = WorkerSeedingDataLoader(dataset=dummy_dataset, batch_size=1)
  dummy_creator = DatasetCreator(dataloader=dummy_loader, dataset_length=1)

  # Return the dummy dataset creator
  return dummy_creator

# Builds transforms lists from input data
def _build_transform_list(parent, transform_data_list) -> list[Transform]:
  # Initialize the transform list
  transform_data_list_by_parent = [tf for tf in transform_data_list if tf['parent'] == parent]

  # Assemble each transform in the list
  transform_list = []
  for transform_item in transform_data_list_by_parent:
    # Get the class of transform to build
    transform_type = torchsig_transform_map()[transform_item['name']]

    # Parse all parameters received
    parameters = dict()
    for name, param in transform_item['parameters'].items():
      match param['type']:
        case 'null' | 'bool' | 'int' | 'str' | 'list[str]':
          parameters[name] = param['value']
        case 'float':
          parameters[name] = float(param['value'])
        case 'transforms':
          inner_transform_list = _build_transform_list(transform_item['id'], transform_data_list)
          if transform_item['name'] == 'RandomApply':
            parameters['transform'] = Compose(transforms=inner_transform_list)
          else:
            parameters['transforms'] = inner_transform_list
        case _:
          raise(Exception('Invalid Type Value'))

    # Build the transform and add it to the list
    transform = transform_type(**parameters)
    transform_list.append(transform)

  # Return the transform list
  return transform_list

# Builds a custom TorchSig dataset
def torchsig_custom_dataset(metadata_dict, generation_dict, transforms_dict, seed):
  # Get the impairments and its transforms information
  impairment_level = generation_dict['impairments']
  impairments = Impairments(impairment_level)
  component_transforms = [impairments.signal_transforms]
  transforms = [impairments.dataset_transforms]

  # Get the remaining transforms and add them to the transforms list
  configured_transforms = _build_transform_list('', transforms_dict)
  transforms = transforms + configured_transforms

  # Build the dataset
  dataset = TorchSigIterableDataset(
    signal_generators=[],
    metadata=metadata_dict,
    transforms=transforms,
    component_transforms=component_transforms,
    target_labels=None,
    seed=seed,
  )

  # Get the signal generators and add them to the dataset
  generators_list = generation_dict['generators']
  for generator_dict in generators_list:
    next_generator = lookup_signal_generator_by_string(generator_dict['id'])
    dataset.add_signal_generator(next_generator, likelihood=generator_dict['likelihood'])

  # Return the built dataset generator
  return dataset

# Builds a custom TorchSig dataset creator
def torchsig_custom_dataloader(dataset, dataset_dict):
  # Assemble the dataset creator
  dataloader = WorkerSeedingDataLoader(dataset)
  dataloader.collate_fn = identity_collate_fn
  creator = DatasetCreator(
    dataloader=dataloader,
    root=dataset_dict['root'],
    dataset_length=dataset_dict['length'],
    overwrite=dataset_dict['overwrite'],
    multithreading=dataset_dict['multithreading'],
  )

  # Return the built TorchSig dataset creator
  return creator

# Updates the dataset YAML file for a dataset
def update_dataset_yaml(dataset_creator):
  write_dict_to_yaml(
    dataset_creator.dataset_info_filepath,
    dataset_creator.get_dataset_info_dict(
      dataset_length=dataset_creator.items_written,
      original_target_labels=None,
    )
  )

# Updates the writer YAML file for a dataset
def update_writer_yaml(dataset_creator, complete: bool):
  write_dict_to_yaml(
    dataset_creator.writer_info_filepath,
    dataset_creator.get_writer_info_dict(
      complete=complete
    )
  )