import { useGetDatasetDefaultsQuery } from "@/api/api-slice";
import { useAppSelector } from "@/store/hooks";
import { selectDatasetServerHostname } from "@/features/dataset-form/dataset-slice";
import DataLoadingSpinner from "@/components/form-parts/DataLoadingSpinner";
import {
  DatasetFormSeedInput,
  DatasetFormLengthInput,
  DatasetFormFilenameStringInput,
  DatasetFormLocationInput,
  DatasetFormOverwriteCheckbox,
  DatasetFormMultithreadingCheckbox
} from "@/features/dataset-form/DatasetControls";

import Form from "react-bootstrap/Form";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Alert from "react-bootstrap/Alert";

// Contains the dataset creator form tab to display to the user
export default function DatasetForm() {
  // Get the dataset defaults
  const { isLoading } = useGetDatasetDefaultsQuery();
  const hostname = useAppSelector(state => selectDatasetServerHostname(state));

  // Return the loading screen if the data is not available
  if (isLoading) return <DataLoadingSpinner />;

  // Return the dataset creator form tab if the data is available
  return (
    <Form onSubmit={(event) => event.preventDefault()}>
      <Row>
        <Col>
          <Alert variant="info">
            Datasets are written in HDF5 format to a folder on the machine running the server
            {hostname && <> (<strong>{hostname}</strong>)</>}, and are kept after the server stops.
          </Alert>
        </Col>
      </Row>
      <Row><Col><DatasetFormSeedInput id="seed" /></Col></Row>
      <Row><Col><DatasetFormLengthInput id="dataset_length" /></Col></Row>
      <Row><Col><DatasetFormLocationInput id="location" /></Col></Row>
      <Row><Col><DatasetFormFilenameStringInput id="filename" /></Col></Row>
      <Row>
        <Col xs="auto"><DatasetFormOverwriteCheckbox id="overwrite" /></Col>
        <Col xs="auto"><DatasetFormMultithreadingCheckbox id="multithreading" /></Col>
      </Row>
    </Form>
  );
}