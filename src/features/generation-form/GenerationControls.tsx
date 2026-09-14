import { useAppSelector, useAppDispatch } from "@/store/hooks";
import {
  selectGenerationDetail,
  selectGeneratorOptions,
  selectAllGenerators,
  selectGeneratorIds,
  selectImpairments,
  addGenerator,
  setImpairments,
  setGeneratorLikelihoodById,
  removeGenerator
} from "@/features/generation-form/generation-slice";
import { FormOptionSelect } from "@/components/form-parts/FormControls";

import { useState } from "react";
import Button from "react-bootstrap/Button";
import Card from "react-bootstrap/Card";
import Form from "react-bootstrap/Form";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Alert from "react-bootstrap/Alert";
import { XLg } from "react-bootstrap-icons";

// Stores the impairments options
const impairmentsOptions = [
  "Level 0: Simulates a perfect digital environment, with no impairments",
  "Level 1: Simulates a cabled environment, with transit impairments",
  "Level 2: Simulates a wireless environment, with transit and channel impairments",
];

// Creates a generation form impairments select field to display to the user
export function GenerationFormImpairmentsSelect({ id }: { id: string }) {
  // Get the details for this input field
  const { label, hint } = useAppSelector(state => selectGenerationDetail(state, id));

  // Get the current store value and dispatch function
  const valueIndex = useAppSelector(state => selectImpairments(state));
  const impairments = impairmentsOptions[valueIndex];
  const dispatch = useAppDispatch();

  // Define the dispatch function to call when the selection is changed
  function onGenerationFormImpairmentsSelectChange (newImpairmentsString: string) {
    const newImpairments = impairmentsOptions.indexOf(newImpairmentsString);
    if (newImpairments >= 0) {
      dispatch(setImpairments(newImpairments));
    }
  }

  // Return the generation form impairments select field
  return (
    <FormOptionSelect
      id={id}
      values={impairmentsOptions}
      value={impairments}
      onChange={onGenerationFormImpairmentsSelectChange}
      label={label}
      hint={hint}
    />
  );
}

// Creates generation form generator select fields to display to the user
export function GenerationFormGeneratorSelect({ id }: { id: string }) {
  // Get the full lists for the select fields to go through
  const generatorOptions = useAppSelector(state => selectGeneratorOptions(state));
  const groupList = Object.keys(generatorOptions);

  // Get the current list of generators
  const generatorsList = useAppSelector(state => selectGeneratorIds(state));

  // Set the state for the generator select fields
  const [group, setGroup] = useState(groupList[0]);
  const [generator, setGenerator] = useState(generatorOptions[group][0]);
  const [error, setError] = useState("");

  // Define the functions to call when the selections are changed
  const dispatch = useAppDispatch();
  function onGenerationFormGroupSelectChange (newGroup: string) {
    setGroup(newGroup);
    setGenerator(generatorOptions[newGroup][0]);
  }
  function onGenerationFormGeneratorSelectChange (newGenerator: string) {
    setGenerator(newGenerator);
  }

  // Define the function to determine if the selected generator can be added to the list
  function generatorisValid(newGenerator: string) {
    // Check that the generators list can fit the "ALL" generator
    if (newGenerator === "all" && generatorsList.length > 0) {
      setError("Error: Contained generator already selected.");
      return false;
    }

    // Check that the generators list can fit all families
    if (groupList.includes(generator) && generatorOptions[newGenerator].filter(gen => generatorsList.includes(gen)).length > 0) {
      setError("Error: Contained generator already selected.");
      return false;
    }

    // Check that the generators list can fit all generators
    const generatorFamily = groupList.filter(grp => generatorOptions[grp].includes(newGenerator))[0];
    if (generatorsList.includes("all") || generatorsList.includes(generatorFamily)) {
      setError("Error: Containing generator already selected.");
      return false;
    }

    // Return true and clear the error, since all checks have passed
    setError("");
    return true;
  }

  // Return the generation form generator select fields
  return (
    <>
      <FormOptionSelect
      id={id + "-group"}
      values={groupList}
      value={group}
      onChange={onGenerationFormGroupSelectChange}
      />
      <FormOptionSelect
      id={id + "-generator"}
      values={generatorOptions[group]}
      value={generator}
      onChange={onGenerationFormGeneratorSelectChange}
      />
      <Button onClick={() => {
        if (generatorisValid(generator)) {
          dispatch(addGenerator(generator));
        }
      }}>
        Add Generator
      </Button>
      {error && <Alert variant="warning" className="mt-3">{error}</Alert>}
    </>
  );
}

// Creates a generator bubble to display to the user
function GeneratorBubble({ id, likelihood }: { id: string, likelihood: number }) {
  // Get the dispatch function from the store
  const dispatch = useAppDispatch();

  // Create an aria label for the bubble label
  const bubbleLabel = "likelihood-" + id;

  // Return the generator bubble
  return (
    <Col md="auto" className="pb-3">
      <Card className="p-3">
        <Row className="flex-nowrap mb-3 align-items-center">
          <Col className="me-auto d-flex text-fade">
            <p className="mb-0">{id.toUpperCase()}</p>
          </Col>
          <Col xs="auto">
            <Button
              variant="outline-secondary"
              className="pt-0"
              onClick={() => dispatch(removeGenerator(id))}
            >
              <XLg />
            </Button>
          </Col>
        </Row>
        <Row className="flex-nowrap align-items-center">
          <Col className="me-auto d-flex flex-grow-0">
            <p id={bubbleLabel} className="mb-0">{"Likelihood"}</p>
          </Col>
          <Col>
            <Form.Control
              id={id}
              aria-label={id}
              aria-describedby={bubbleLabel}
              value={likelihood}
              onChange={(e) => {
                const newLikelihood = Number(e.currentTarget.value);
                if (!isNaN(newLikelihood)) {
                  dispatch(setGeneratorLikelihoodById(id, newLikelihood));
                }
                else {
                  console.log("Error: Attempted to create a non-number likelihood!");
                }
              }}
            />
          </Col>
        </Row>
      </Card>
    </Col>
  );
}

// Creates a set of generator bubbles to display to the user
export function GeneratorBubbleWindow() {
  // Get the current list of generators
  const generatorsList = useAppSelector(state => selectAllGenerators(state));

  // Display the generators as bubbles
  const generatorList = generatorsList.map(g => (
    <GeneratorBubble
      key={g.id}
      id={g.id}
      likelihood={g.likelihood}
    />
  ));

  // Display a placeholder if there are no bubbles
  const generatorListPlaceholder = <p>No Generators Selected</p>;

  // Return the collection of generator bubbles
  return (
    <Card className="mt-3">
      <Container fluid className="p-3 pb-0">
        <Row>
          { generatorList.length > 0 ? generatorList : generatorListPlaceholder }
        </Row>
      </Container>
    </Card>
  );
}