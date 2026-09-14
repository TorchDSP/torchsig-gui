// Imports globally used styles
import "bootstrap/dist/css/bootstrap.min.css";
import "@/app/globals.css";

// Imports React components and hooks
import StoreProvider from "@/providers/StoreProvider";
import LayoutHeader from "@/components/layout-marginals/LayoutHeader";
import LayoutFooter from "@/components/layout-marginals/LayoutFooter";

// Adds the metadata for the tab appearance
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "TorchSigGUI",
  description: "A user interface to generate signal datasets",
};

// Defines the root component used to contain page components
// (This component must contain the <html> and <body> elements by Next.js specification)
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  // Set the default theme
  const defaultMode = "dark";

  // Return the layout component to display to the user
  return (
    <StoreProvider>
      <html lang="en" className="h-100">
        <body className="flex-window" data-bs-theme={defaultMode}>
          <header className="flex-fixed">
            <LayoutHeader defaultMode={defaultMode} />
          </header>
          <main className="flex-fill">
            {children}
          </main>
          <footer className="flex-fixed">
            <LayoutFooter />
          </footer>
        </body>
      </html>
    </StoreProvider>
  );
}
