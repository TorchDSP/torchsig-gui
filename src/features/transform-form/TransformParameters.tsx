import { useAppSelector } from "@/store/hooks";
import {
  selectTransformById,
  selectWIPTransformById
} from "@/features/transform-form/transform-slice";
import {
  TransformAddEditIntegerInput,
  TransformAddEditFloatInput,
  TransformAddEditCheckbox,
  TransformAddEditSelect,
  TransformAddEditMultiSelect
} from "@/features/transform-form/TransformAddEditControls";

// Creates a Transform parameters list to display to the user
export default function TransformParameters({ id, editMode }: { id: string, editMode: boolean }) {
  // Get the transform options and the current transform option
  const transform = useAppSelector(state => selectTransformById(state, id));
  const wipTransform = useAppSelector(state => selectWIPTransformById(state, id));

  // Create the list of transform parameters in read-only mode
  let readModeTransformParametersList: React.ReactNode[] = [];
  if (transform) {
    Object.entries(transform.parameters).forEach(([paramName, param]) => {
      readModeTransformParametersList.push(
        <li key={paramName}>
          {paramName}: {param.value?.toString()}
        </li>
      );
    });
  }

  // Create the list of transform parameters in edit mode
  let editModeTransformParametersList: React.ReactNode[] = [];
  if (!wipTransform) {
    editModeTransformParametersList.push(<p key={"nullTransform"}>No Transform Found</p>);
  }
  else {
    Object.entries(wipTransform.parameters).forEach(([paramName, param]) => {
      let parameter = null;
      switch (param.type) {
        case "list[str]":
          parameter = <TransformAddEditMultiSelect key={paramName} id={id} paramName={paramName} param={param.value} />
          break;
        case "str":
          parameter = <TransformAddEditSelect key={paramName} id={id} paramName={paramName} param={param.value} />
          break;
        case "int":
          parameter = <TransformAddEditIntegerInput key={paramName} id={id} paramName={paramName} param={param.value} />
          break;
        case "float":
          parameter = <TransformAddEditFloatInput key={paramName} id={id} paramName={paramName} param={param.value} />
          break;
        case "bool":
          parameter = <TransformAddEditCheckbox key={paramName} id={id} paramName={paramName} param={param.value} />
          break;
        default:
          break;
      }

      editModeTransformParametersList.push(parameter);
    });
  }

  // Return the transform parameters list
  return editMode ? editModeTransformParametersList : <ul>{readModeTransformParametersList}</ul>;
}