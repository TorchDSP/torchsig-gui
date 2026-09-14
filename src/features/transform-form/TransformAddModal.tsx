import { useAppSelector, useAppDispatch } from "@/store/hooks";
import {
  selectTransformOptions,
  resetTransformById,
  selectWIPTransformById,
  removeTransform,
  saveTransform
} from "@/features/transform-form/transform-slice";
import TransformParameters from "@/features/transform-form/TransformParameters";
import { FormOptionSelect } from "@/components/form-parts/FormControls";

import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";

// Creates a Transform addition modal to display to the user
export default function TransformAddModal({ id, parent, show, setId }: { id: string, parent: string, show: boolean, setId: CallableFunction }) {
  // Get the dispatch function
  const dispatch = useAppDispatch();

  // Get the transform options and the current transform option
  const transformOptions = useAppSelector(state => selectTransformOptions(state));
  const transform = useAppSelector(state => selectWIPTransformById(state, id));

  // Define the function to call when the selection is changed
  // - When the selection is changed, the work-in-progress transform should update to the new type
  function onTransformFormTransformSelectChange (newTransform: string) {
    dispatch(resetTransformById(id, newTransform));
  }

  // Return the Transform addition modal
  return (
    <Modal
      show={show}
      onHide={() => {
        dispatch(removeTransform(id));
        setId("");
      }}
      backdrop="static"
      fullscreen="md-down"
      keyboard={false}
    >
      <Modal.Header closeButton>
        <Modal.Title>Add New Transform</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <FormOptionSelect
          id="transform-select"
          values={Object.keys(transformOptions)}
          value={transform?.ttype ?? "AWGN"}
          onChange={onTransformFormTransformSelectChange}
        />
        <TransformParameters id={id} editMode={true} />
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={() => {
          dispatch(removeTransform(id));
          setId("");
        }}>
          Cancel
        </Button>
        <Button variant="primary" onClick={() => {
          dispatch(saveTransform(id));
          setId("");
        }}>
          Add Transform
        </Button>
      </Modal.Footer>
    </Modal>
  );
}