import { RecordMap, TypedValue } from "@/types/shared-types";
import { DatasetDefaults } from "@/types/dataset-types";
import { AsyncInfo } from "@/types/dataset-list-types";

import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react"

// Updates the base URL by what mode the webpage is running on
const baseUrl = process.env.NODE_ENV === "development" ? "http://localhost:8000" : "";

// Builds the websocket URL by what mode the webpage is running on
// - In production, the server hosting the page also hosts the websocket, so use the page's own host and protocol
function buildWebSocketLink() {
  if (process.env.NODE_ENV === "development") {
    return "ws://localhost:8000/ws";
  }
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return protocol + "//" + window.location.host + "/ws";
}

// Defines the API slice object
export const apiSlice = createApi({
  // Define where the state of the cached data is found in the store
  reducerPath: "api",

  // Define the method for starting API requests and the common destination
  baseQuery: fetchBaseQuery({ baseUrl: baseUrl + "/api" }),

  // Define the different available requests
  endpoints: builder => ({
    getMetadataDefaults: builder.query<RecordMap<number>, void>({
      query: () => "/metadata-defaults"
    }),
    getGeneratorOptions: builder.query<RecordMap<string[]>, void>({
      query: () => "/generator-options"
    }),
    getTransformOptions: builder.query<RecordMap<RecordMap<TypedValue>>, void>({
      query: () => "/transform-options"
    }),
    getDatasetDefaults: builder.query<DatasetDefaults, void>({
      query: () => "/dataset-defaults"
    }),
    postWriteSample: builder.mutation<unknown, unknown>({
      query: (fullData) => ({
        url: "/write-sample",
        method: "POST",
        body: fullData
      })
    }),
    postWriteDataset: builder.mutation<unknown, unknown>({
      query: (fullData) => ({
        url: "/write-dataset",
        method: "POST",
        body: fullData
      })
    }),
    postCancelDataset: builder.mutation<unknown, string>({
      query: (fileID) => ({
        url: "/cancel-dataset/" + fileID,
        method: "DELETE"
      })
    }),
    getLiveUpdates: builder.query<AsyncInfo, void>({
      // Return an empty map initially
      queryFn: async () => ({ data: { "sampleFilename": "", "datasetMap": {} } }),

      // Update the cache entry keep time to close the socket sooner
      keepUnusedDataFor: 3,

      // Manage a websocket to watch for updates from the server
      async onCacheEntryAdded(_arg, { cacheDataLoaded, cacheEntryRemoved, updateCachedData }) {
        // Create a websocket connection when the cache subscription starts
        const ws = new WebSocket(buildWebSocketLink());

        try {
          // Wait for the initial query to resolve
          await cacheDataLoaded

          // Create a listener function to update the cache entry when the server delivers an update
          const listener = (event: MessageEvent<string>) => {
            const asyncData = JSON.parse(event.data);
            updateCachedData(draft => {
              if (asyncData.type && typeof asyncData.type === "string") {
                switch (asyncData.type) {
                  case "spectrogram":
                    draft.sampleFilename = asyncData.update;
                    break;
                  case "file":
                    draft.datasetMap = asyncData.update;
                    break;
                  default:
                    break;
                }
              }
              return draft;
            });
          }

          // Bind the listener function to the client socket
          ws.addEventListener('message', listener);
        } catch {
          // NO-OP for race conditions where the cache entry is removed and immmediately reloaded
        }

        // Wait until the cache subscription is no longer active
        await cacheEntryRemoved;

        // Close the socket connection when the cache subscription ends
        ws.close();
      }
    })
  })
});

// Exports the auto-generated hooks for the endpoints
export const {
  useGetMetadataDefaultsQuery,
  useGetGeneratorOptionsQuery,
  useGetTransformOptionsQuery,
  useGetDatasetDefaultsQuery,
  usePostWriteSampleMutation,
  usePostWriteDatasetMutation,
  usePostCancelDatasetMutation,
  useGetLiveUpdatesQuery
} = apiSlice;

// Exports utility functions for building URLs
export function buildImageLink(filename: string) {
  return baseUrl + "/images/" + filename;
}