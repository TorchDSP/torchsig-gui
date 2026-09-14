import metadataJSON from "@/features/metadata-form/metadata-input-details.json";

import { apiSlice } from "@/api/api-slice";
import { RecordMap, InputDetail } from "@/types/shared-types";
import { RootState } from "@/store/store";
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

// Sets the initial state of the state slice
const initialMetadataDetails: RecordMap<number> = {};
const initialMetadata = {
  metadata: initialMetadataDetails,
  metadataLabels: metadataJSON as RecordMap<InputDetail>
}

// Creates the state slice for the metadata form
const metadataFormSlice = createSlice({
  // Name the slice
  name: "metadataForm",

  // Set the initial state slice data
  initialState: initialMetadata,

  // Add the reducer functions to the state slice
  reducers: {
    // Sets the value of the data for a given entry
    // [setMetadataFormEntry(entry, value)]
    setMetadataFormEntry: {
      reducer(state, action: PayloadAction<{ entry: string, value: number }>) {
        const { entry, value } = action.payload;
        state.metadata[entry] = value;
      },
      prepare(entry: string, value: number) {
        return { payload: { entry: entry, value: value } }
      }
    }
  },

  // Add an extra reducer to trigger when the metadata is fetched
  extraReducers: (builder) => {
    builder.addMatcher(
      apiSlice.endpoints.getMetadataDefaults.matchFulfilled,
      (state, action) => {
        state.metadata = action.payload;
        return state;
      }
    );
  }
});

// Exports the selectors, actions, and reducer function of the metadata state slice
export const selectMetadataDetail = (state: RootState, id: string) => state.metadataForm.metadataLabels[id];

export const selectAllMetadataFormEntries = (state: RootState) => state.metadataForm.metadata;
export const selectMetadataFormEntry = (state:RootState, id: string) => state.metadataForm.metadata[id];

export const { setMetadataFormEntry } = metadataFormSlice.actions;

export default metadataFormSlice.reducer;