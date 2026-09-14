import { apiSlice } from "@/api/api-slice";
import { RecordMap, TypedValue } from "@/types/shared-types";
import { Transform } from "@/types/transform-types";
import { RootState } from "@/store/store";
import { numberComparer, generateSortUpdates } from "@/features/transform-form/transform-utils";

import {
  createSlice,
  createEntityAdapter,
  PayloadAction
} from "@reduxjs/toolkit";

// Creates entity adapters to track the transforms that the user has selected and edited
const transformsAdapter = createEntityAdapter<Transform>({ sortComparer: (a, b) => numberComparer(a.index, b.index) });
const wipTransformsAdapter = createEntityAdapter<Transform>({ sortComparer: (a, b) => numberComparer(a.index, b.index) });

// Sets the initial state of the transform slice
const initialTransformOptions: RecordMap<RecordMap<TypedValue>> = {};

const initialTransforms = {
  transformOptions: initialTransformOptions,
  transforms: transformsAdapter.getInitialState(),
  wipTransforms: wipTransformsAdapter.getInitialState()
};

// Creates the state slice for the transform form
const transformFormSlice = createSlice({
  // Name the slice
  name: "transformForm",

  // Set the initial state slice data
  initialState: initialTransforms,

  // Add the reducer functions to the state slice
  reducers: {
    // Adds a new transform to the work-in-progress transforms list
    // [addTransform(type, parameters)]
    addTransform: {
      reducer(state, action: PayloadAction<{ id: string, parent: string }>) {
        // Get the location to add the new transform in the list
        const index = state.wipTransforms.ids.length;

        // Get the default transform details for the new transform
        const { id, parent } = action.payload;
        const defaultTtype = Object.keys(state.transformOptions)[0];
        const defaultParameters = state.transformOptions[defaultTtype];

        // Create the new transform
        const newTransform: Transform = {
          id: id,
          parent: parent,
          index: index,
          ttype: defaultTtype,
          parameters: defaultParameters
        };

        // Add the new transform to the list
        wipTransformsAdapter.addOne(state.wipTransforms, newTransform);
      },
      prepare(id: string, parent: string) {
        return { payload: { id: id, parent: parent } }
      }
    },
    // Sets the parameters of a transform in the work-in-progress transforms list
    // [setTransformParameterById(id, name, value)]
    setTransformParameterById: {
      reducer(state, action: PayloadAction<{ id: string, name: string, value: TypedValue }>) {
        // Create a new set of parameters to apply the updated parameter
        const { id, name, value } = action.payload;
        let newParameters = { ...state.wipTransforms.entities[id].parameters };
        newParameters[name] = value;

        // Update the transform to use the new set of parameters
        wipTransformsAdapter.updateOne(state.wipTransforms, { id: id, changes: { parameters: newParameters } });
      },
      prepare(id: string, name: string, value: TypedValue) {
        return { payload: { id: id, name: name, value: value } }
      }
    },
    // Resets a transform in the work-in-progress transforms list to be a different type
    // [resetTransformById(id, ttype)]
    resetTransformById: {
      reducer(state, action: PayloadAction<{ id: string, ttype: string }>) {
        const { id, ttype } = action.payload;
        wipTransformsAdapter.updateOne(state.wipTransforms, { id: id, changes: { ttype: ttype, parameters: state.transformOptions[ttype] } });
      },
      prepare(id: string, ttype: string) {
        return { payload: { id: id, ttype: ttype } }
      }
    },
    // Resorts the transforms in the transforms lists
    // [resortTransforms(source, target)]
    resortTransforms: {
      reducer(state, action: PayloadAction<{ source: number, target: number }>) {
        // Get the sort updates for the transform lists
        const { source, target } = action.payload;
        const sortUpdates = generateSortUpdates(state.transforms.ids, source, target);

        // Apply the sort updates to the transform lists
        wipTransformsAdapter.updateMany(state.wipTransforms, sortUpdates);
        transformsAdapter.updateMany(state.transforms, sortUpdates);
      },
      prepare(source: number, target: number) {
        return { payload: { source: source, target: target } }
      }
    },
    // Removes a transform from the transforms lists
    // [removeTransform(id)]
    removeTransform(state, action: PayloadAction<string>) {
      // Gets the id of the removed transform
      const removedId = action.payload;

      // Updates the indeces for all transforms in the transforms list
      // - The indeces should be arranged as if the removed transform was placed at the end ([0, length-2] with length-1 removed)
      if (state.transforms.ids.includes(removedId)) {
        const removedIndex = state.transforms.entities[removedId].index;
        const resortUpdates = generateSortUpdates(state.transforms.ids, removedIndex, state.transforms.ids.length - 1);
        transformsAdapter.updateMany(state.transforms, resortUpdates);
      }

      // Updates the indeces for all transforms in the work-in-progress transforms list
      // - The indeces should be arranged as if the removed transform was placed at the end ([0, length-2] with length-1 removed)
      if (state.wipTransforms.ids.includes(removedId)) {
        const removedWIPIndex = state.wipTransforms.entities[removedId].index;
        const resortUpdates = generateSortUpdates(state.wipTransforms.ids, removedWIPIndex, state.wipTransforms.ids.length - 1);
        wipTransformsAdapter.updateMany(state.wipTransforms, resortUpdates);
      }

      // Removes the transform from the transform lists
      transformsAdapter.removeOne(state.transforms, action.payload);
      wipTransformsAdapter.removeOne(state.wipTransforms, action.payload);
    },
    // Saves a work-in-progress transform in the transform list
    // [saveTransform(id)]
    saveTransform(state, action:PayloadAction<string>) {
      const savedId = action.payload;
      transformsAdapter.upsertOne(state.transforms, state.wipTransforms.entities[savedId]);
    },
    // Reverts a work-in-progress transform to match its saved copy in the transform list, if one exists
    // - If no corresponding transform exists, it deletes the work-in-progress transform instead
    // [revertTransform(id)]
    revertTransform(state, action:PayloadAction<string>) {
      const cancelledId = action.payload;
      if (state.transforms.ids.includes(cancelledId)) {
        wipTransformsAdapter.upsertOne(state.wipTransforms, state.transforms.entities[cancelledId]);
      }
      else {
        removeTransform(cancelledId);
      }
    }
  },

  // Add an extra reducer to trigger when the transform options data is fetched
  extraReducers: (builder) => {
    builder.addMatcher(
      apiSlice.endpoints.getTransformOptions.matchFulfilled,
      (state, action) => {
        state.transformOptions = action.payload;
        return state;
      }
    );
  }
});

// Exports the transform options of the transform state slice
export const selectTransformOptions = (state: RootState) => state.transformForm.transformOptions;
export const selectTransformOption = (state: RootState, id: string, paramName: string) => state.transformForm.wipTransforms.entities[id].parameters[paramName];

// Exports the transforms selectors of the transform state slice
export const {
  selectAll: selectAllTransforms,
  selectById: selectTransformById,
  selectIds: selectTransformIds
} = transformsAdapter.getSelectors((state: RootState) => state.transformForm.transforms);

export const {
  selectAll: selectAllWIPTransforms,
  selectById: selectWIPTransformById,
  selectIds: selectWIPTransformIds
} = wipTransformsAdapter.getSelectors((state: RootState) => state.transformForm.wipTransforms);

// Exports the actions and reducer function of the transform state slice
export const {
  addTransform,
  setTransformParameterById,
  resetTransformById,
  resortTransforms,
  removeTransform,
  saveTransform,
  revertTransform
} = transformFormSlice.actions;

export default transformFormSlice.reducer;