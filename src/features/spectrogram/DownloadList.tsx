import { DownloadInfo } from "@/types/download-types";
import { RecordMap } from "@/types/shared-types";
import { usePostCancelDatasetMutation, buildDownloadLink } from "@/api/api-slice";

import React from "react";

import Card from "react-bootstrap/Card";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import ProgressBar from "react-bootstrap/ProgressBar";
import Button from "react-bootstrap/Button";

// Contains the download item to display to the user
function DownloadItem({ downloadID, download, cancelFunc }: { downloadID: string, download: DownloadInfo, cancelFunc: CallableFunction }) {
  // Return the download item
  return (
    <Card className="p-3 mb-3">
      <Row>
        <Col><p>{download.filepath}</p></Col>
        <Col><ProgressBar now={download.progress / download.total * 100} /></Col>
        <Col>
          <Button
            as="a"
            href={buildDownloadLink(downloadID)}
            download={download.filepath}
            disabled={download.progress !== download.total}
          >
            Download
          </Button>
        </Col>
        <Col>
          <Button
            as="a"
            onClick={() => cancelFunc(downloadID)}
            variant="danger"
          >
            Cancel
          </Button>
        </Col>
      </Row>
      <Row><p className="mb-0">{download.current_status}</p></Row>
    </Card>
  );
}

// Contains the download list to display to the user
export default function DownloadList({ downloadMap }: { downloadMap: RecordMap<DownloadInfo> }) {
  // Get the trigger function for cancelling datasets
  const [ cancel, {} ] = usePostCancelDatasetMutation();

  // Create the list of download items in the list, based on the map contents
  const downloadList: React.ReactNode[] = [];
  Object.entries(downloadMap).forEach(([downloadID, download]) => {
    const downloadItem = <DownloadItem key={downloadID} downloadID={downloadID} download={download} cancelFunc={cancel}/>;
    downloadList.push(downloadItem);
  });

  // Return the download list
  return (
    <>
      {downloadList}
    </>
  );
}