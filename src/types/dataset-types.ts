// Defines a type for storing dataset creation details
interface DatasetDetails {
  seed?: number,
  length?: number,
  root?: string,
  overwrite: boolean,
  multithreading: boolean,
};

// Exports all dataset types
export type { DatasetDetails };