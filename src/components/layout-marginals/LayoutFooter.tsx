"use client"

import Navbar from "react-bootstrap/Navbar";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";

// Contains the footer to display to the user
export default function LayoutFooter() {
  // Create the footer
  return (
    <Navbar className="bg-body-tertiary">
      <Container fluid className="justify-content-center">
        <Row>
          <Col><a href="https://torchsig.com">TorchSig Main Site</a></Col>
          <Col><a href="https://torchsig.readthedocs.io/latest">TorchSig Documentation</a></Col>
          <Col><a href="https://github.com/TorchDSP/torchsig">TorchSig GitHub</a></Col>
          <Col><a href="#">TorchSig GUI GitHub</a></Col>
        </Row>
      </Container>
    </Navbar>
  );
}