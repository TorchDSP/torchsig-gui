// Defines a type for storing dataset creation details
interface DatasetDetails {
  seed?: number,
  length?: number,
  root?: string,
  location?: string,
  overwrite: boolean,
  multithreading: boolean,
};

// Defines a type for the dataset defaults sent by the server
// - hostname names the machine running the server, where the save location is
interface DatasetDefaults extends DatasetDetails {
  hostname: string,
};

// Exports all dataset types
export type { DatasetDetails, DatasetDefaults };