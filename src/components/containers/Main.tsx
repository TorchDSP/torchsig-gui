"use client"

import FormSelector from "@/components/containers/FormSelector";
import SpectrogramContainer from "@/features/spectrogram/SpectrogramContainer";

import Container from "react-bootstrap/Container";

// Contains the homepage component to be displayed to the user
export default function Main() {
  return (
    <Container fluid className="p-3 dashboard-grid">
      <FormSelector />
      <SpectrogramContainer />
    </Container>
  );
}