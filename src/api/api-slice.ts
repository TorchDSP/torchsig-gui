import { RecordMap, TypedValue } from "@/types/shared-types";
import { DatasetDetails } from "@/types/dataset-types";
import { AsyncInfo } from "@/types/download-types";

import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react"

// Updates the base URL by what mode the webpage is running on
const baseUrl = process.env.NODE_ENV === "development" ? "http://localhost:8000" : "";

// Updates the websocket port by what mode the webpage is running on
const prodPort = (typeof window === "undefined") ? "8000" : window.location.port;
const wsPort = process.env.NODE_ENV === "development" ? "8000" : prodPort;

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
    getDatasetDefaults: builder.query<DatasetDetails, void>({
      query: () => "/dataset-defaults"
    }),
    postWriteSample: builder.mutation<any, any>({
      query: (fullData) => ({
        url: "/write-sample",
        method: "POST",
        body: fullData
      })
    }),
    postWriteDataset: builder.mutation<any, any>({
      query: (fullData) => ({
        url: "/write-dataset",
        method: "POST",
        body: fullData
      })
    }),
    postCancelDataset: builder.mutation<any, string>({
      query: (fileID) => ({
        url: "/cancel-dataset/" + fileID,
        method: "DELETE"
      })
    }),
    getDownloads: builder.query<AsyncInfo, void>({
      // Return an empty map initially
      queryFn: async () => ({ data: { "sampleFilename": "", "downloadMap": {} } }),

      // Update the cache entry keep time to close the socket sooner
      keepUnusedDataFor: 3,

      // Manage a websocket to watch for updates from the server
      async onCacheEntryAdded(_arg, { cacheDataLoaded, cacheEntryRemoved, updateCachedData }) {
        // Create a websocket connection when the cache subscription starts
        const ws = new WebSocket("ws://localhost:" + wsPort + "/ws");

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
                    draft.downloadMap = asyncData.update;
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
  useGetDownloadsQuery
} = apiSlice;

// Exports utility functions for building URLs
export function buildImageLink(filename: string) {
  return baseUrl + "/images/" + filename;
}
export function buildDownloadLink(id: string) {
  return baseUrl + "/api/download-dataset/" + id;
}