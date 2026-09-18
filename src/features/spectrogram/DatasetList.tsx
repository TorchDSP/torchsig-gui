import { DatasetStatus } from "@/types/dataset-list-types";
import { RecordMap } from "@/types/shared-types";
import { usePostCancelDatasetMutation } from "@/api/api-slice";
import { useAppSelector } from "@/store/hooks";
import { selectDatasetServerHostname } from "@/features/dataset-form/dataset-slice";

import React, { useState } from "react";

import Card from "react-bootstrap/Card";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import ProgressBar from "react-bootstrap/ProgressBar";
import Button from "react-bootstrap/Button";

// Gets the dataset name from its folder path, which may use either path separator depending on the server
function getDatasetName(filepath: string) {
  return filepath.split(/[\\/]/).pop() || filepath;
}

// Contains a line of text with a button that copies it
// - The text can also be selected by hand, since the clipboard is unavailable on pages that are not served securely
function CopyableText({ text }: { text: string }) {
  // Keep track of whether the text was just copied
  const [ copied, setCopied ] = useState(false);

  // Copy the text and show that it was copied for a moment
  async function copyText() {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // NO-OP when the clipboard is unavailable; the text can still be selected by hand
    }
  }

  // Return the text and copy button
  return (
    <Row className="align-items-center mb-2">
      <Col className="text-break"><code className="user-select-all">{text}</code></Col>
      <Col xs="auto">
        <Button size="sm" variant="outline-secondary" onClick={copyText}>
          {copied ? "Copied" : "Copy"}
        </Button>
      </Col>
    </Row>
  );
}

// Contains the dataset item to display to the user
// - Shows where the dataset is written, its progress, and, once finished, how to load it
function DatasetItem({ datasetID, dataset, hostname, cancelFunc }: { datasetID: string, dataset: DatasetStatus, hostname: string, cancelFunc: CallableFunction }) {
  // Find the state of the dataset
  const failed = dataset.complete && !dataset.ready;

  // Pick the action for the dataset
  // - Unfinished datasets are cancelled and their partial files deleted
  // - Finished datasets are only removed from the list, keeping their files
  const action = !dataset.complete ? "Cancel" : failed ? "Delete" : "Remove from List";

  // Return the dataset item
  return (
    <Card className="p-3 mb-3">
      <Row className="align-items-center mb-2">
        <Col><strong>{getDatasetName(dataset.filepath)}</strong></Col>
        <Col xs="auto">
          <Button
            size="sm"
            variant={dataset.ready ? "outline-secondary" : "danger"}
            onClick={() => cancelFunc(datasetID)}
          >
            {action}
          </Button>
        </Col>
      </Row>
      <ProgressBar
        className="mb-2"
        now={dataset.progress / dataset.total * 100}
        variant={dataset.ready ? "success" : failed ? "danger" : undefined}
      />
      <p className="mb-2">{dataset.current_status}</p>
      <p className="mb-1 small text-body-secondary">
        {dataset.ready ? "Saved to" : "Writing to"} this folder{hostname && " on " + hostname}:
      </p>
      <CopyableText text={dataset.filepath} />
      {dataset.ready && (
        <>
          <p className="mb-1 small text-body-secondary">Load it with TorchSig:</p>
          <CopyableText text={"StaticTorchSigDataset(root=r\"" + dataset.filepath + "\")"} />
        </>
      )}
    </Card>
  );
}

// Contains the list of datasets being written or already written to display to the user
export default function DatasetList({ datasetMap }: { datasetMap: RecordMap<DatasetStatus> }) {
  // Get the trigger function for cancelling and removing datasets
  const [ cancel, {} ] = usePostCancelDatasetMutation();

  // Get the name of the machine running the server, where the datasets are written
  const hostname = useAppSelector(state => selectDatasetServerHostname(state));

  // Create the list of dataset items in the list, based on the map contents
  const datasetList: React.ReactNode[] = [];
  Object.entries(datasetMap).forEach(([datasetID, dataset]) => {
    const datasetItem = <DatasetItem key={datasetID} datasetID={datasetID} dataset={dataset} hostname={hostname} cancelFunc={cancel}/>;
    datasetList.push(datasetItem);
  });

  // Return the dataset list
  return (
    <>
      {datasetList}
    </>
  );
}
