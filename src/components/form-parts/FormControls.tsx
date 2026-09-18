import customSelectStyle, { FormOption } from "@/components/form-parts/select-style";

import Form from "react-bootstrap/Form";
import Badge from "react-bootstrap/Badge";
import OverlayTrigger from "react-bootstrap/OverlayTrigger";
import { OverlayInjectedProps } from "react-bootstrap/Overlay";
import Tooltip from "react-bootstrap/Tooltip";

import Select, { MultiValue } from "react-select";

// Creates a hint badge to display a hint tooltip to the user
function HintBadge({ hint }: { hint: string }) {
  // Create the function to render the tooltip
  const renderTooltip = (props: OverlayInjectedProps) => (
    <Tooltip id="button" {...props}>
      {hint}
    </Tooltip>
  );

  // Return a hint Badge that will show the tooltip when hovered over for 0.5 seconds
  return (
    <OverlayTrigger
      placement="right"
      delay={{ show: 500, hide: 500 }}
      overlay={renderTooltip}
    >
      <Badge bg="secondary">?</Badge>
    </OverlayTrigger>
  );
}

// Creates a label with an optional hint badge
function FormFieldLabel({ label, hint="" }: { label: string, hint?: string }) {
  return (
    <>
      {label}
      {hint && " "}
      {hint && <HintBadge hint={hint}/>}
    </>
  )
}

// Defines a function for resetting the input for invalid changes
type FormControlElement = HTMLInputElement | HTMLTextAreaElement;
function removeInvalidCharacters(e: React.InputEvent<FormControlElement>, isInt: boolean) {
  // Get the changed value before and after removing invalid characters
  const oldValue = e.currentTarget.value;
  const newFloatValue = e.currentTarget.value.replace(/[^\d-\.]/g, '').replace(/(?!^)-/g, '').replace(/(?<=\..*)\./g, '');
  const newIntValue = e.currentTarget.value.replace(/[^\d-]/g, '').replace(/(?!^)-/g, '');
  const newValue = isInt ? newIntValue : newFloatValue;

  // If invalid characters are present, remove them and reset the cursor to after the valid characters added
  if (oldValue != newValue) {
    const oldCursorPosition = e.currentTarget.selectionStart ?? 0;
    const newCursorPosition = oldCursorPosition + newValue.length - oldValue.length;

    e.currentTarget.value = newValue;
    e.currentTarget.setSelectionRange(newCursorPosition, newCursorPosition);
  }
}

// Creates a form input field to display to the user
export function FormInput({ id, value, isInt, onChange, label, hint }: { id: string, value: string, isInt?: boolean, onChange: CallableFunction, label?: string, hint?: string }) {
  // Return the form input with a label and hint badge, if they exist
  return (
    <Form.Group className="mb-3" controlId={id}>
      {label && <Form.Label><FormFieldLabel label={label} hint={hint} /></Form.Label>}
      <Form.Control
        defaultValue={value}
        placeholder={"Enter " + label + "..."}
        onChange={(e) => onChange(e)}
        onInput={(e) => removeInvalidCharacters(e, isInt ?? false)}
      />
    </Form.Group>
  );
}

// Creates a form file input field to display to the user
export function FormFileInput({ id, value, onChange, label, hint }: { id: string, value?: string, onChange: CallableFunction, label?: string, hint?: string }) {
  // Return the form file input with a label, hint badge, placeholder, and starting value, if they exist
  return (
    <Form.Group className="mb-3" controlId={id}>
      {label && <Form.Label><FormFieldLabel label={label} hint={hint} /></Form.Label>}
      <Form.Control
        defaultValue={value}
        placeholder={"Enter " + label + "..."}
        onChange={(e) => onChange(e)}
      />
    </Form.Group>
  );
}

// Creates a form checkbox to display to the user
export function FormCheckbox({ id, checked, onChange, label, hint }: { id: string, checked: boolean, onChange: CallableFunction, label?: string, hint?: string }) {
  // Return the checkbox with a label and hint badge, if they exist
  return (
    <Form.Group className="mb-3" controlId={id}>
      <Form.Check
        type="checkbox"
        label={label && <FormFieldLabel label={label} hint={hint} />}
        checked={checked}
        onChange={(e) => onChange(e)}
      />
    </Form.Group>
  );
}

// Defines a converter function for handling onChange output
function onChangeWrapper(onChange: CallableFunction) {
  return (value: FormOption | null): void => {
    onChange(value?.value ?? "");
  };
}

// Creates a form select field to display to the user
export function FormOptionSelect({ id, values, value, onChange, label, hint }: { id: string, values: string[], value: string, onChange: CallableFunction, label?: string, hint?: string }) {
  // Update the value and values list to be something that the react-select dropdown can read
  // - The value must be obtained from the list since react-select only uses object references for comparisons
  const options: FormOption[] = values.map(val => ({ value: val, label: val }));
  const valueObj = options.find(opt => opt.value === value);

  // Return the select field with a label and hint badge, if they exist
  return (
    <Form.Group className="mb-3" controlId={id}>
      {label && <Form.Label><FormFieldLabel label={label} hint={hint} /></Form.Label>}
      <Select
        id={id}
        options={options}
        value={valueObj}
        onChange={onChangeWrapper(onChange)}
        styles={customSelectStyle<false>()}
      />
    </Form.Group>
  );
}

// Defines a converter function for handling onChange output
function onMultiChangeWrapper(onChange: CallableFunction) {
  return (multiValue: MultiValue<FormOption>): void => {
    const newValues : string[] = [];
    multiValue.forEach(value => newValues.push(value.value));
    onChange(newValues ?? []);
  };
}

// Creates a form multi-select field to display to the user
export function FormOptionMultiSelect({ id, values, multiValue, onChange, label, hint }: { id: string, values: string[], multiValue: string[], onChange: CallableFunction, label?: string, hint?: string }) {
  // Update the values list to be something that the react-select dropdown can read
  // - The value must be obtained from the list since react-select only uses object references for comparisons
  const options: FormOption[] = values.map(val => ({ value: val, label: val }));
  const valuesObj: MultiValue<FormOption> = options.filter(opt => multiValue.includes(opt.value));

  // Return the transform form multi-select field
  return (
    <Form.Group className="mb-3" controlId={id}>
      {label && <Form.Label><FormFieldLabel label={label} hint={hint} /></Form.Label>}
      <Select
        isMulti
        id={id}
        options={options}
        value={valuesObj}
        onChange={onMultiChangeWrapper(onChange)}
        styles={customSelectStyle<true>()}
      />
    </Form.Group>
  );
}