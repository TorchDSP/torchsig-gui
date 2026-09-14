import { AppStore } from "@/store/store";
import { useAppStore } from "@/store/hooks";
import { usePostWriteSampleMutation, usePostWriteDatasetMutation, useGetDownloadsQuery } from "@/api/api-slice";

import SpectrogramImage from "@/features/spectrogram/SpectrogramImage";
import DownloadList from "@/features/spectrogram/DownloadList";

import { useState } from "react";

import Card from "react-bootstrap/Card";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Button from "react-bootstrap/Button";

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

// Contains all spectrogram details to display to the user
export default function SpectrogramContainer() {
  // Get a reference to the store
  // - This is needed to avoid rerendering on updates to the form state
  const storeRef = useAppStore();

  // Get the current downloads info
  const { data } = useGetDownloadsQuery();

  // Get the trigger functions for writing sample spectrograms and dataset files
  const [ saveNewSample, {} ] = usePostWriteSampleMutation();
  const [ saveNewDataset, {} ] = usePostWriteDatasetMutation();

  // Keep track of whether the next spectrogram image has loaded
  const [ hasLoaded, setHasLoaded ] = useState(true);

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
            onClick={ () => {
              const formState = extractFormState(storeRef);
              saveNewDataset(formState);
            }}
          >
            Generate Dataset
          </Button>
        </Col>
      </Row>
      <DownloadList downloadMap={data?.downloadMap ?? {}} />
    </Card>
  );
}