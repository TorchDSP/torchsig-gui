import { RecordMap } from "@/types/shared-types";

// Defines a type for storing the status of a dataset being written or already written
// - filepath is the dataset folder on the machine running the server
type DatasetStatus = {
  current_status: string,
  progress: number,
  total: number,
  filepath: string,
  complete: boolean,
  ready: boolean,
};

// Defines a type for storing sample and dataset information
type AsyncInfo = {
  sampleFilename: string,
  datasetMap: RecordMap<DatasetStatus>,
};

// Exports all dataset list types
export type { DatasetStatus, AsyncInfo };
