import { useAppSelector, useAppDispatch } from "@/store/hooks";
import {
  selectTransformById,
  removeTransform,
  saveTransform,
  revertTransform
} from "@/features/transform-form/transform-slice";
import TransformParameters from "@/features/transform-form/TransformParameters";

import { useState } from "react";
import { useSortable } from "@dnd-kit/react/sortable";
import { directionBiased } from "@dnd-kit/collision";

import Card from "react-bootstrap/Card";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Button from "react-bootstrap/Button";
import { Trash } from "react-bootstrap-icons";

// Creates a sortable Transform bubble to display to the user
export default function TransformSortable({ id }: { id: string }) {
  // Get the edit mode for this Transform
  const [editMode, setEditMode] = useState(false);

  // Get the information and the sortable reference for this Transform
  const { index, ttype, parameters } = useAppSelector(state => selectTransformById(state, id));
  const { ref } = useSortable({ id, index, collisionDetector: directionBiased });

  // Get the dispatch function
  const dispatch = useAppDispatch();

  // Return the sortable Transform bubble
  return (
    <Row className="my-3">
      <Card ref={ref}>
        <Container fluid className="p-3">
          <Row className="flex-nowrap">
            <Col className="me-auto d-flex align-items-center text-fade">
              <p className="mb-0">{ttype}</p>
            </Col>
            <Col xs="auto">
              <Button
                variant="danger"
                className="pt-0"
                onClick={() => dispatch(removeTransform(id))}
              >
                <Trash />
              </Button>
            </Col>
          </Row>
          { Object.entries(parameters).length > 0 &&
            <Row className="mt-3">
              <Col><TransformParameters id={id} editMode={editMode} /></Col>
              <Col xs={"auto"}><Button onClick={() => setEditMode(editMode => !editMode)}>Edit</Button></Col>
            </Row>
          }
          { Object.entries(parameters).length > 0 && editMode &&
            <Row className="justify-content-end">
              <Col xs="auto">
                <Button variant="secondary" onClick={() => {
                  dispatch(revertTransform(id));
                  setEditMode(false);
                }}>
                  Cancel
                </Button>
              </Col>
              <Col xs="auto">
                <Button variant="primary" onClick={() => {
                  dispatch(saveTransform(id));
                  setEditMode(false);
                }}>
                  Save Transform
                </Button>
              </Col>
            </Row>
          }
        </Container>
      </Card>
    </Row>
  );
}