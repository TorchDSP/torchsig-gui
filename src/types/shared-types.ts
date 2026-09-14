// Defines a type for storing form data
type RecordMap<Type> = {
  [index: string]: Type,
};

// Defines a type for storing form input details
type InputDetail = {
  label?: string,
  hint?: string,
};

// Defines a type for tracking the type of a variable
type TypedValue = (
  { type: 'null', value: null } |
  { type: 'bool', value: boolean } |
  { type: 'int', value: number } |
  { type: 'float', value: number } |
  { type: 'str', value: string } |
  { type: 'list[str]', value: string[] } |
  { type: 'transforms', value: string[] }
);

// Exports all shared types
export type { RecordMap, InputDetail, TypedValue };