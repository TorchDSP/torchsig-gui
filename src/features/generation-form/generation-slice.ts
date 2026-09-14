import generationJSON from "@/features/generation-form/generation-input-details.json";

import { apiSlice } from "@/api/api-slice";
import { RecordMap, InputDetail } from "@/types/shared-types";
import { RootState } from "@/store/store";
import {
  createSlice,
  createEntityAdapter,
  PayloadAction
} from "@reduxjs/toolkit";

// Creates an entity adapter to track the generators that the user has selected
interface Generator {
  id: string,
  likelihood: number
};
const generatorsAdapter = createEntityAdapter<Generator>();

// Sets the initial state of the generation slice
const initialImpairments = 0;
const initialGeneratorOptions: RecordMap<string[]> = {};
const initialGenerators = { ids: ["all"], entities: { all: { id: "all", likelihood: 1 }}};

const initialGeneration = {
  impairments: initialImpairments,
  generatorOptions: initialGeneratorOptions,
  generators: generatorsAdapter.getInitialState(initialGenerators),
  generationLabels: generationJSON as RecordMap<InputDetail>
};

// Creates the state slice for the generation form
const generationFormSlice = createSlice({
  // Name the slice
  name: "generationForm",

  // Set the initial state slice data
  initialState: initialGeneration,

  // Add the reducer functions to the state slice
  reducers: {
    // Adds a new generator to the generators list
    // [addGenerator(id)]
    addGenerator(state, action: PayloadAction<string>) {
      generatorsAdapter.addOne(state.generators, { id: action.payload, likelihood: 1 });
    },
    // Sets the likelihood of a generator in the generators list
    // [setGeneratorLikelihoodById(id, likelihood)]
    setGeneratorLikelihoodById: {
      reducer(state, action: PayloadAction<{ id: string, likelihood: number }>) {
        const { id, likelihood } = action.payload;
        generatorsAdapter.updateOne(state.generators, { id: id, changes: { likelihood: likelihood } })
      },
      prepare(id: string, likelihood: number) {
        return { payload: { id: id, likelihood: likelihood } }
      }
    },
    // Removes a generator from the generators list
    // [removeGenerator(id)]
    removeGenerator(state, action: PayloadAction<string>) {
      generatorsAdapter.removeOne(state.generators, action.payload);
    },
    // Sets the value of the data for a given index
    // [setImpairments(impairments)]
    setImpairments(state, action: PayloadAction<number>) {
      state.impairments = action.payload;
    }
  },

  // Add an extra reducer to trigger when the generator options data is fetched
  extraReducers: (builder) => {
    builder.addMatcher(
      apiSlice.endpoints.getGeneratorOptions.matchFulfilled,
      (state, action) => {
        state.generatorOptions = action.payload;
        return state;
      }
    );
  }
});

// Exports the impairments, generator options, and generators selectors of the generation state slice
export const selectGenerationDetail = (state: RootState, id: string) => state.generationForm.generationLabels[id];

export const selectImpairments = (state: RootState) => state.generationForm.impairments;
export const selectGeneratorOptions = (state: RootState) => state.generationForm.generatorOptions;
export const selectGeneratorFamilyById = (state: RootState, id: string) => state.generationForm.generatorOptions[id];

export const {
  selectAll: selectAllGenerators,
  selectById: selectGeneratorById,
  selectIds: selectGeneratorIds
} = generatorsAdapter.getSelectors((state: RootState) => state.generationForm.generators);

// Exports the actions and reducer function of the generation state slice
export const { addGenerator, setGeneratorLikelihoodById, removeGenerator, setImpairments } = generationFormSlice.actions;

export default generationFormSlice.reducer;