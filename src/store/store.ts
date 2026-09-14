import { configureStore } from "@reduxjs/toolkit";

import metadataFormReducer from "@/features/metadata-form/metadata-slice";
import generationFormReducer from "@/features/generation-form/generation-slice";
import transformFormReducer from "@/features/transform-form/transform-slice";
import datasetFormReducer from "@/features/dataset-form/dataset-slice";
import { apiSlice } from "@/api/api-slice";

// Defines a function to return a per-user store to track global state for each user
export const makeStore = () => configureStore({
  // Add the reducer functions to update each state slice
  reducer: {
    metadataForm: metadataFormReducer,
    generationForm: generationFormReducer,
    transformForm: transformFormReducer,
    datasetForm: datasetFormReducer,
    [apiSlice.reducerPath]: apiSlice.reducer,
  },

  // Add the API middleware
  middleware: getDefaultMiddleware =>
    getDefaultMiddleware().concat(apiSlice.middleware)
});

// Exports the types of the store, the store state, and the store dispatch function
export type AppStore = ReturnType<typeof makeStore>;
export type RootState = ReturnType<AppStore["getState"]>;
export type AppDispatch = AppStore["dispatch"];