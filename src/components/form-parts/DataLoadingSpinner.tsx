import Container from "react-bootstrap/Container";
import Spinner from "react-bootstrap/Spinner";

// Creates a loading spinner to display to the user while data is loading
export default function DataLoadingSpinner() {
  return (
    <Container className="text-center">
      <h2 className="p-3">
        <Spinner animation="border" />
        {" "}Loading Data...
      </h2>
    </Container>
  );
}