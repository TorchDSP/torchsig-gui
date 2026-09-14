import { useAppSelector, useAppDispatch } from "@/store/hooks";
import { TypedValue } from "@/types/shared-types";
import { selectTransformOption, setTransformParameterById } from "@/features/transform-form/transform-slice";
import {
  FormInput,
  FormCheckbox,
  FormOptionSelect,
  FormOptionMultiSelect
} from "@/components/form-parts/FormControls";

import { ChangeEvent } from "react";

// Creates a transform form integer input field to display to the user
export function TransformAddEditIntegerInput({ id, paramName, param }: { id: string, paramName: string, param: number }) {
  // Get the dispatch function
  const dispatch = useAppDispatch();

  // Define the dispatch function to call when the input is changed
  function onTransformIntegerInputChange(e: ChangeEvent<HTMLInputElement, Element>) {
    const newValue = Number(e.currentTarget.value);
    const newParam = { type: "int", value: isNaN(newValue) ? 0 : newValue } as TypedValue;
    dispatch(setTransformParameterById(id, paramName, newParam));
  }

  // Return the transform integer form input
  return (
    <FormInput
      id={id + "-" + paramName}
      value={param.toString()}
      isInt={true}
      onChange={onTransformIntegerInputChange}
      label={paramName}
    />
  );
}

// Creates a transform form float input field to display to the user
export function TransformAddEditFloatInput({ id, paramName, param }: { id: string, paramName: string, param: number }) {
  // Get the dispatch function
  const dispatch = useAppDispatch();

  // Define the dispatch function to call when the input is changed
  function onTransformFloatInputChange(e: ChangeEvent<HTMLInputElement, Element>) {
    const newValue = Number(e.currentTarget.value);
    const newParam = { type: "float", value: isNaN(newValue) ? 0 : newValue } as TypedValue;
    dispatch(setTransformParameterById(id, paramName, newParam));
  }

  // Return the transform float form input
  return (
    <FormInput
      id={id + "-" + paramName}
      value={param.toString()}
      isInt={false}
      onChange={onTransformFloatInputChange}
      label={paramName}
    />
  );
}

// Creates a transform form checkbox to display to the user
export function TransformAddEditCheckbox({ id, paramName, param }: { id: string, paramName: string, param: boolean }) {
  // Get the dispatch function
  const dispatch = useAppDispatch();

  // Define the dispatch function to call when the checkbox is changed
  function onTransformCheckboxChange(e: ChangeEvent<HTMLInputElement, Element>) {
    const nextChecked = e.currentTarget.checked;
    const newParam = { type: "bool", value: nextChecked } as TypedValue;
    dispatch(setTransformParameterById(id, paramName, newParam));
  }

  // Return the transform form checkbox
  return (
    <FormCheckbox
      id={id + "-" + paramName}
      checked={param}
      onChange={onTransformCheckboxChange}
      label={paramName}
    />
  );
}

// Creates a transform form select field to display to the user
export function TransformAddEditSelect({ id, paramName, param }: { id: string, paramName: string, param: string }) {
  // Define the dispatch function to call when the selection is changed
  const dispatch = useAppDispatch();
  function onTransformAddEditSelectChange(newSelection: string) {
    const newParam = { type: "str", value: newSelection } as TypedValue;
    dispatch(setTransformParameterById(id, paramName, newParam));
  }

  // Return the transform form select field
  return (
    <FormOptionSelect
      id={id + "-" + paramName}
      values={["white", "pink", "red"]}
      value={param}
      onChange={onTransformAddEditSelectChange}
      label={paramName}
    />
  );
}

// Creates a transform form multi-select field to display to the user
export function TransformAddEditMultiSelect({ id, paramName, param }: { id: string, paramName: string, param: string[] }) {
  // Define the dispatch function to call when the multi-selection is changed
  const dispatch = useAppDispatch();
  function onTransformAddEditMultiSelectChange(newSelection: string[]) {
    const newParam = { type: "list[str]", value: newSelection } as TypedValue;
    dispatch(setTransformParameterById(id, paramName, newParam));
  }

  // Get the full options list from the store, if possible
  const optionsType = useAppSelector(state => selectTransformOption(state, id, paramName));
  const options : string[] = optionsType.type === "list[str]" ? optionsType.value : [];

  // Return the transform form multi-select field
  return (
    <FormOptionMultiSelect
      id={id + "-" + paramName}
      values={options}
      multiValue={param}
      onChange={onTransformAddEditMultiSelectChange}
      label={paramName}
    />
  );
}