import datasetJSON from "@/features/dataset-form/dataset-input-details.json";

import { apiSlice } from "@/api/api-slice";
import { DatasetDetails } from "@/types/dataset-types";
import { RecordMap, InputDetail } from "@/types/shared-types";
import { RootState } from "@/store/store";
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

// Sets the initial state of the state slice
const initialDatasetDetails : DatasetDetails = { overwrite: true, multithreading: true }
const initialDataset = {
  dataset: initialDatasetDetails,
  datasetLabels: datasetJSON as RecordMap<InputDetail>
};

// Creates the state slice for the dataset form
const datasetFormSlice = createSlice({
  // Name the slice
  name: "datasetForm",

  // Set the initial state slice data
  initialState: initialDataset,

  // Add the reducer functions to the state slice
  reducers: {
    // Sets the dataset randomizer seed
    // [setDatasetFormSeedEntry(length)]
    setDatasetFormSeedEntry(state, action: PayloadAction<number | undefined>) {
      state.dataset.seed = action.payload;
    },
    // Sets the dataset length
    // [setDatasetFormLengthEntry(length)]
    setDatasetFormLengthEntry(state, action: PayloadAction<number>) {
      state.dataset.length = action.payload;
    },
    // Sets the dataset file name
    // [setDatasetFormFilenameEntry(filename)]
    setDatasetFormFilenameEntry(state, action: PayloadAction<string>) {
      state.dataset.root = action.payload;
    },
    // Sets the dataset overwrite setting
    // [setDatasetFormOverwriteEntry(overwrite)]
    setDatasetFormOverwriteEntry(state, action: PayloadAction<boolean>) {
      state.dataset.overwrite = action.payload;
    },
    // Sets the dataset multithreading setting
    // [setDatasetFormMultithreadingEntry(multithreading)]
    setDatasetFormMultithreadingEntry(state, action: PayloadAction<boolean>) {
      state.dataset.multithreading = action.payload;
    }
  },

  // Add an extra reducer to trigger when the dataset creator data is fetched
  extraReducers: (builder) => {
    builder.addMatcher(
      apiSlice.endpoints.getDatasetDefaults.matchFulfilled,
      (state, action) => {
        state.dataset = action.payload;
        return state;
      }
    );
  }
});

// Exports the selectors of the dataset state slice
export const selectDatasetDetail = (state: RootState, id: string) => state.datasetForm.datasetLabels[id];

export const selectAllDatasetFormEntries = (state: RootState) => state.datasetForm.dataset;
export const selectDatasetFormSeedEntry = (state:RootState) => state.datasetForm.dataset.seed;
export const selectDatasetFormLengthEntry = (state:RootState) => state.datasetForm.dataset.length;
export const selectDatasetFormRootEntry = (state:RootState) => state.datasetForm.dataset.root;
export const selectDatasetFormOverwriteEntry = (state:RootState) => state.datasetForm.dataset.overwrite;
export const selectDatasetFormMultithreadingEntry = (state:RootState) => state.datasetForm.dataset.multithreading;

// Exports the actions and reducer function of the dataset state slice
export const {
  setDatasetFormSeedEntry,
  setDatasetFormLengthEntry,
  setDatasetFormFilenameEntry,
  setDatasetFormOverwriteEntry,
  setDatasetFormMultithreadingEntry
} = datasetFormSlice.actions;

export default datasetFormSlice.reducer;