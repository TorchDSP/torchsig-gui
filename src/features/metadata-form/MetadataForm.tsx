import { useGetMetadataDefaultsQuery } from "@/api/api-slice";
import DataLoadingSpinner from "@/components/form-parts/DataLoadingSpinner";
import { MetadataFormInput } from "@/features/metadata-form/MetadataControls";

import Form from "react-bootstrap/Form";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";

// Contains the metadata form tab to display to the user
export default function MetadataForm() {
  // Get the metadata defaults
  const { isLoading } = useGetMetadataDefaultsQuery();

  // Return the loading screen if the data is not available
  if (isLoading) return <DataLoadingSpinner />;

  // Return the metadata form tab if the data is available
  return (
    <Form onSubmit={(event) => event.preventDefault()}>
      <Row><Col><MetadataFormInput id="num_iq_samples_dataset" isInt={true} /></Col></Row>
      <Row>
        <Col><MetadataFormInput id="fft_size" isInt={true} /></Col>
        <Col><MetadataFormInput id="fft_stride" isInt={true} /></Col>
      </Row>
      <Row><Col><MetadataFormInput id="sample_rate" /></Col></Row>
      <Row><Col><MetadataFormInput id="cochannel_overlap_probability" /></Col></Row>
      <Row>
        <Col><MetadataFormInput id="num_signals_min" isInt={true} /></Col>
        <Col><MetadataFormInput id="num_signals_max" isInt={true} /></Col>
      </Row>
      <Row>
        <Col><MetadataFormInput id="snr_db_min" /></Col>
        <Col><MetadataFormInput id="snr_db_max" /></Col>
      </Row>
      <Row>
        <Col><MetadataFormInput id="signal_duration_in_samples_min" /></Col>
        <Col><MetadataFormInput id="signal_duration_in_samples_max" /></Col>
      </Row>
      <Row>
        <Col><MetadataFormInput id="bandwidth_min" /></Col>
        <Col><MetadataFormInput id="bandwidth_max" /></Col>
      </Row>
      <Row>
        <Col><MetadataFormInput id="signal_center_freq_min" /></Col>
        <Col><MetadataFormInput id="signal_center_freq_max" /></Col>
      </Row>
      <Row>
        <Col><MetadataFormInput id="frequency_min" /></Col>
        <Col><MetadataFormInput id="frequency_max" /></Col>
      </Row>
      <Row><Col><MetadataFormInput id="noise_power_db" /></Col></Row>
    </Form>
  );
}