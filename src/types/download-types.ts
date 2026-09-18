import { RecordMap } from "@/types/shared-types";

// Defines a type for storing file information data
type DownloadInfo = {
  current_status: string,
  progress: number,
  total: number,
  filepath: string,
  ready: boolean,
};

// Defines a type for storing sample and file information
type AsyncInfo = {
  sampleFilename: string,
  downloadMap: RecordMap<DownloadInfo>,
};

// Exports all file info types
export type { DownloadInfo, AsyncInfo };