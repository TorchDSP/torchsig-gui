"use client"

import { useState, startTransition } from "react";

import Image from "next/image";

import Container from "react-bootstrap/Container";
import Navbar from "react-bootstrap/Navbar";
import Button from "react-bootstrap/Button";
import { Moon, Sun } from "react-bootstrap-icons";

// Contains the TorchSig logo image
function LogoImage({ imgSrc }: { imgSrc: string }) {
  return (
    <Image
      alt=""
      src={imgSrc}
      width="30"
      height="30"
      className="d-inline-block align-top"
      fetchPriority="high"
    />
  );
}

// Contains the theme button to display to the user
function ThemeButton({ mode, setMode }: { mode: string, setMode: CallableFunction }) {
  // Find the next mode
  const nextMode = mode === "light" ? "dark" : "light";

  // Create a function to set the next mode via updating the DOM manually
  // - CAUTION:
  // - This usually causes issues with React rendering, since the shadow DOM has a chance of going out of sync
  // - But since DOM elements aren't created or destroyed here, this should be fine
  function updateMode() {
    document.body.setAttribute('data-bs-theme', nextMode);
    setMode(nextMode);
  }

  // Create the theme button based on the current mode
  return (
    <Button
      className="pt-0"
      variant={nextMode}
      onClick={() => startTransition(updateMode)}>
      { mode === "light" ? <Moon/> : <Sun/> }
    </Button>
  );
}

// Contains the header to display to the user
export default function LayoutHeader({ defaultMode }: { defaultMode: string }) {
  // Track the current mode
  const [mode, setMode] = useState(defaultMode);

  // Get the logo based on the mode
  const logoImgSrc = mode === "light" ?
    "/torchsig_icon_dodgerblue_black.png" :
    "/torchsig_icon_dodgerblue_white.png";

  // Create the header based on the current mode
  return (
    <Navbar className="bg-body-tertiary">
      <Container className="justify-content-center">
        <Navbar.Brand href="#home">
          <LogoImage imgSrc={logoImgSrc} />
          {" "}TorchSig GUI
        </Navbar.Brand>
        <ThemeButton mode={mode} setMode={setMode} />
      </Container>
    </Navbar>
  );
};