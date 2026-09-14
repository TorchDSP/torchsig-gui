import { useAppSelector, useAppDispatch } from "@/store/hooks";
import {
  selectMetadataDetail,
  selectMetadataFormEntry,
  setMetadataFormEntry
} from "@/features/metadata-form/metadata-slice";
import { FormInput } from "@/components/form-parts/FormControls";

import { ChangeEvent } from "react";

// Creates a metadata form input field to display to the user
export function MetadataFormInput({ id, isInt }: { id: string, isInt?: boolean }) {
  // Get the details for this input field
  const { label, hint } = useAppSelector(state => selectMetadataDetail(state, id));

  // Get the current store value and dispatch function
  const value = useAppSelector(state => selectMetadataFormEntry(state, id));
  const dispatch = useAppDispatch();

  // Define the dispatch function to call when the input is changed
  function onMetadataFormInputChange (e: ChangeEvent<HTMLInputElement, Element>) {
    const newValue = Number(e.currentTarget.value);
    if (!isNaN(newValue)) {
      dispatch(setMetadataFormEntry(id, newValue))
    }
  }

  // Return the metadata form input
  return (
    <FormInput
      id={id}
      value={value.toString()}
      isInt={isInt}
      onChange={onMetadataFormInputChange}
      label={label}
      hint={hint}
    />
  );
}