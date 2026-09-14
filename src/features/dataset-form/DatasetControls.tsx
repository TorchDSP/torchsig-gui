import { useAppSelector, useAppDispatch } from "@/store/hooks";
import {
  selectDatasetDetail,
  selectDatasetFormSeedEntry,
  selectDatasetFormLengthEntry,
  selectDatasetFormOverwriteEntry,
  selectDatasetFormMultithreadingEntry,
  setDatasetFormSeedEntry,
  setDatasetFormLengthEntry,
  setDatasetFormFilenameEntry,
  setDatasetFormOverwriteEntry,
  setDatasetFormMultithreadingEntry
} from "@/features/dataset-form/dataset-slice";
import {
  FormInput,
  FormFileInput,
  FormCheckbox
} from "@/components/form-parts/FormControls";

import { ChangeEvent } from "react";

// Creates a dataset form input field for the seed to display to the user
export function DatasetFormSeedInput({ id }: { id: string }) {
  // Get the details for this input field
  const { label, hint } = useAppSelector(state => selectDatasetDetail(state, id));

  // Get the current store value and dispatch function
  const value = useAppSelector(state => selectDatasetFormSeedEntry(state));
  const dispatch = useAppDispatch();

  // Define the dispatch function to call when the input is changed
  function onDatasetFormInputChange (e: ChangeEvent<HTMLInputElement, Element>) {
    const newValue = Number(e.currentTarget.value);
    if (e.currentTarget.value.length === 0) {
      dispatch(setDatasetFormSeedEntry(undefined))
    }
    else if (!isNaN(newValue)) {
      dispatch(setDatasetFormSeedEntry(newValue))
    }
  }

  // Return the dataset form input
  return (
    <FormInput
      id={id}
      value={value?.toString() ?? ""}
      isInt={true}
      onChange={onDatasetFormInputChange}
      label={label}
      hint={hint}
    />
  );
}

// Creates a dataset form input field for the length to display to the user
export function DatasetFormLengthInput({ id }: { id: string }) {
  // Get the details for this input field
  const { label, hint } = useAppSelector(state => selectDatasetDetail(state, id));

  // Get the current store value and dispatch function
  const value = useAppSelector(state => selectDatasetFormLengthEntry(state));
  const dispatch = useAppDispatch();

  // Define the dispatch function to call when the input is changed
  function onDatasetFormInputChange (e: ChangeEvent<HTMLInputElement, Element>) {
    const newValue = Number(e.currentTarget.value);
    if (!isNaN(newValue)) {
      dispatch(setDatasetFormLengthEntry(newValue))
    }
  }

  // Return the dataset form input
  return (
    <FormInput
      id={id}
      value={value?.toString() ?? ""}
      isInt={true}
      onChange={onDatasetFormInputChange}
      label={label}
      hint={hint}
    />
  );
}

// Creates a dataset form file input field for the root folder to display to the user
export function DatasetFormFilenameStringInput({ id }: { id: string }) {
  // Get the details for this input field
  const { label, hint } = useAppSelector(state => selectDatasetDetail(state, id));

  // Define the dispatch function to call when the file input is changed
  const dispatch = useAppDispatch();
  function onDatasetFormStringInputChange (e: ChangeEvent<HTMLInputElement, Element>) {
    dispatch(setDatasetFormFilenameEntry(e.currentTarget.value.trim()))
  }

  // Return the dataset form file input
  return (
    <FormFileInput
      id={id}
      onChange={onDatasetFormStringInputChange}
      label={label}
      hint={hint}
    />
  );
}

// Creates a dataset form checkbox for the overwrite setting to display to the user
export function DatasetFormOverwriteCheckbox({ id }: { id: string }) {
  // Get the details for this input field
  const { label, hint } = useAppSelector(state => selectDatasetDetail(state, id));

  // Get the current store value and dispatch function
  const value = useAppSelector(state => selectDatasetFormOverwriteEntry(state));
  const dispatch = useAppDispatch();

  // Define the dispatch function to call when the checkbox is changed
  function onDatasetFormCheckboxChange (e: ChangeEvent<HTMLInputElement, Element>) {
    dispatch(setDatasetFormOverwriteEntry(e.currentTarget.checked));
  }

  // Return the dataset form checkbox
  return (
    <FormCheckbox
      id={id}
      checked={value}
      onChange={onDatasetFormCheckboxChange}
      label={label}
      hint={hint}
    />
  );
}

// Creates a dataset form checkbox for the multithreading setting to display to the user
export function DatasetFormMultithreadingCheckbox({ id }: { id: string }) {
  // Get the details for this input field
  const { label, hint } = useAppSelector(state => selectDatasetDetail(state, id));

  // Get the current store value and dispatch function
  const value = useAppSelector(state => selectDatasetFormMultithreadingEntry(state));
  const dispatch = useAppDispatch();

  // Define the dispatch function to call when the checkbox is changed
  function onDatasetFormCheckboxChange (e: ChangeEvent<HTMLInputElement, Element>) {
    dispatch(setDatasetFormMultithreadingEntry(e.currentTarget.checked));
  }

  // Return the dataset form checkbox
  return (
    <FormCheckbox
      id={id}
      checked={value}
      onChange={onDatasetFormCheckboxChange}
      label={label}
      hint={hint}
    />
  );
}