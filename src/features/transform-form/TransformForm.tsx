import { useGetTransformOptionsQuery } from "@/api/api-slice";
import {
  selectTransformIds,
  selectWIPTransformIds,
  addTransform
} from "@/features/transform-form/transform-slice";
import { useAppSelector, useAppDispatch } from "@/store/hooks";
import DataLoadingSpinner from "@/components/form-parts/DataLoadingSpinner";

import TransformAddModal from "@/features/transform-form/TransformAddModal";
import TransformSortable from "@/features/transform-form/TransformSortable";
import TransformDragDropProvider from "@/providers/TransformDragDropProvider";

import { useState } from "react";
import { nanoid } from "@reduxjs/toolkit";

import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Button from "react-bootstrap/Button";

// Contains the transform form tab to display to the user
export default function TransformForm() {
  // Get the transform options
  const { isLoading } = useGetTransformOptionsQuery();

  // Get the dispatch function and the lists of transform ids
  const dispatch = useAppDispatch();
  const ids = useAppSelector(state => selectTransformIds(state));
  const wipIds = useAppSelector(state => selectWIPTransformIds(state));

  // Define the controls to open the transform add modal
  // - Opening the modal generates a new work-in-progress transform with a new id
  const [currentId, setCurrentId] = useState("");
  const openModal = () => {
    let newId;
    do { newId = nanoid(); } while(wipIds.includes(newId));
    dispatch(addTransform(newId, ""));
    setCurrentId(newId);
  }

  // Return the loading screen if the data is not available
  if (isLoading) return <DataLoadingSpinner />;

  // Return the transform form tab if the data is available
  return (
    <Container fluid>
      <Row className="d-inline-flex"><Button onClick={openModal}>Add Transform</Button></Row>
      <TransformAddModal id={currentId} show={currentId != ""} setId={setCurrentId} />
      <TransformDragDropProvider>
        { ids.map(id => <TransformSortable key={id} id={id} />) }
      </TransformDragDropProvider>
    </Container>
  );
}