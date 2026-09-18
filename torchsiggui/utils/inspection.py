from inspect import getmembers, isclass, signature, Parameter
from re import compile

# Creates a regex pattern to search for strings within single quotes
# This helps with types used as annotations that display like this: <class '[type]'>
CLASS_TYPE_PATTERN = compile(r"'(.*)'")

# Retrieves all classes from a module
def get_classes(input_module):
  # Create a dictionary for all classes retrieved from the module
  class_map = ({
    class_name: class_obj for class_name, class_obj in
    getmembers(input_module) if isclass(class_obj)
  })

  # Return the dictionary
  return class_map

# Retrieves class parameters from a class constructor
def get_class_parameters(input_class):
  # Get the class signature
  class_signature = signature(input_class)

  # Get the class parameters from the signature
  class_parameters = dict()
  for name, param in class_signature.parameters.items():
    # Skip all non-explicit parameters
    if name == 'self': continue
    if param.kind != param.POSITIONAL_OR_KEYWORD: continue

    # Get the parameter type, after normalizating the annotation
    annotation = str(param.annotation)
    type_match = CLASS_TYPE_PATTERN.search(annotation)
    param_type = type_match.group(1) if type_match else annotation

    # Skip all tuple and null default parameters
    if 'empty' in param_type: continue
    if 'tuple' in param_type: continue
    if 'None' in param_type: continue

    # Get the default parameter value
    param_value = param.default if param.default not in [Parameter.empty, None] else ''

    # Add the next parameter to the class parameter list
    class_parameters[name] = { 'type': param_type, 'value': param_value }

  # Return the class parameters
  return class_parameters