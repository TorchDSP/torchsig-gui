"use client"

import { useState } from "react"
import { Provider } from "react-redux"
import { makeStore } from "@/store/store"

// Provides the store for the application to read from
export default function StoreProvider({ children }: { children: React.ReactNode }) {
  // Create the store instance the first time this renders and keep it across renders
  const [store] = useState(makeStore);

  // Return the Provider component to fetch the store from
  return (
    <Provider store={store}>
      {children}
    </Provider>
  );
}
