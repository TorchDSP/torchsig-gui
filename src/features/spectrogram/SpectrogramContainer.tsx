import { AppStore } from "@/store/store";
import { useAppStore } from "@/store/hooks";
import { usePostWriteSampleMutation, usePostWriteDatasetMutation, useGetLiveUpdatesQuery } from "@/api/api-slice";

import SpectrogramImage from "@/features/spectrogram/SpectrogramImage";
import DatasetList from "@/features/spectrogram/DatasetList";

import { useState } from "react";

import Card from "react-bootstrap/Card";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Button from "react-bootstrap/Button";
import Alert from "react-bootstrap/Alert";

// Defines a function to reformat the relevant details from the store
function extractFormState(storeRef: AppStore) {
  // Get the current state
  const state = storeRef.getState();

  // Extract all relevant information from the state
  const metadata = state.metadataForm.metadata;
  const generation = {
    impairments: state.generationForm.impairments,
    generators: state.generationForm.generators.ids.map((id) => state.generationForm.generators.entities[id])
  };
  const transforms = state.transformForm.transforms.ids.map((id) => {
    const entity = state.transformForm.transforms.entities[id];
    return { id: entity.id, parent: entity.parent, name: entity.ttype, parameters: entity.parameters };
  });
  const { seed, ...dataset } = state.datasetForm.dataset;

  // Return the formatted result
  return ({
    metadata: metadata,
    generation: generation,
    transforms: transforms,
    seed: seed,
    dataset: dataset,
  });
}

// Gets a readable message from a failed API request
// - FastAPI errors carry their message in the "detail" field of the response body
function getErrorMessage(error: unknown) {
  if (error && typeof error === "object" && "data" in error) {
    const data = (error as { data: unknown }).data;
    if (data && typeof data === "object" && "detail" in data && typeof data.detail === "string") {
      return data.detail;
    }
  }
  return "The dataset could not be started. Check the server console for details.";
}

// Contains all spectrogram details to display to the user
export default function SpectrogramContainer() {
  // Get a reference to the store
  // - This is needed to avoid rerendering on updates to the form state
  const storeRef = useAppStore();

  // Get the current sample and dataset info
  const { data } = useGetLiveUpdatesQuery();

  // Get the trigger functions for writing sample spectrograms and dataset files
  const [ saveNewSample, {} ] = usePostWriteSampleMutation();
  const [ saveNewDataset, {} ] = usePostWriteDatasetMutation();

  // Keep track of whether the next spectrogram image has loaded
  const [ hasLoaded, setHasLoaded ] = useState(true);

  // Keep track of the error from the last dataset request, if any
  const [ datasetError, setDatasetError ] = useState("");

  // Return the spectrogram details
  return (
    <Card className="p-3 flex-scroll">
      <Row className="mb-3"><SpectrogramImage filename={data?.sampleFilename ?? ""} hasLoaded={hasLoaded} setHasLoaded={setHasLoaded} /></Row>
      <Row className="mb-3">
        <Col md="auto">
          <Button
            onClick={ () => {
              setHasLoaded(false);
              const formState = extractFormState(storeRef);
              saveNewSample(formState);
            }}
          >
            Generate Sample
          </Button>
        </Col>
        <Col md="auto">
          <Button
            onClick={ async () => {
              const formState = extractFormState(storeRef);
              try {
                setDatasetError("");
                await saveNewDataset(formState).unwrap();
              } catch (error) {
                setDatasetError(getErrorMessage(error));
              }
            }}
          >
            Generate Dataset
          </Button>
        </Col>
      </Row>
      {datasetError && (
        <Alert variant="danger" dismissible onClose={() => setDatasetError("")}>
          {datasetError}
        </Alert>
      )}
      <DatasetList datasetMap={data?.datasetMap ?? {}} />
    </Card>
  );
}