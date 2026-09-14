import MetadataForm from "@/features/metadata-form/MetadataForm";
import GenerationForm from "@/features/generation-form/GenerationForm";
import TransformForm from "@/features/transform-form/TransformForm";
import DatasetForm from "@/features/dataset-form/DatasetForm";

import Card from "react-bootstrap/Card";
import Tabs from "react-bootstrap/Tabs";
import Tab from "react-bootstrap/Tab";

// Contains the tabbed form sections to display to the user
export default function FormSelector() {
  // Return the tabbed form sections
  return (
    <Card>
      <Tabs
        defaultActiveKey="metadata"
        id="dataset-config"
      >
        <Tab className="p-3" eventKey="metadata" title="Metadata">
          <MetadataForm />
        </Tab>
        <Tab className="p-3" eventKey="generation" title="Generation">
          <GenerationForm />
        </Tab>
        <Tab className="p-3" eventKey="transform" title="Transforms">
          <TransformForm />
        </Tab>
        <Tab className="p-3" eventKey="creator" title="Creator">
          <DatasetForm />
        </Tab>
      </Tabs>
    </Card>
  );
}