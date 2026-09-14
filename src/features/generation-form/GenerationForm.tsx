import { useGetGeneratorOptionsQuery } from "@/api/api-slice";
import DataLoadingSpinner from "@/components/form-parts/DataLoadingSpinner";
import {
  GenerationFormImpairmentsSelect,
  GenerationFormGeneratorSelect,
  GeneratorBubbleWindow
} from "@/features/generation-form/GenerationControls";

import Form from "react-bootstrap/Form";
import Row from "react-bootstrap/Row";

// Contains the generation form tab to display to the user
export default function GenerationForm() {
  // Get the generation options
  const { isLoading } = useGetGeneratorOptionsQuery();

  // Return the loading screen if the data is not available
  if (isLoading) return <DataLoadingSpinner />;

  // Return the transform form tab if the data is available
  return (
    <Form onSubmit={(event) => event.preventDefault()}>
      <Row><Form.Label column="lg">Impairments</Form.Label></Row>
      <Row><GenerationFormImpairmentsSelect id="impairments" /></Row>
      <Row><Form.Label column="lg">Signal Generators</Form.Label></Row>
      <GenerationFormGeneratorSelect id="generators" />
      <GeneratorBubbleWindow />
    </Form>
  );
}