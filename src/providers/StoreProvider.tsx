"use client"

import { useRef } from "react"
import { Provider } from "react-redux"
import { makeStore, AppStore } from "@/store/store"

// Provides the store for the application to read from
export default function StoreProvider({ children }: { children: React.ReactNode }) {
  // Create the store as a ref
  const storeRef = useRef<AppStore | null>(null);
  if (!storeRef.current) {
    // Create the store instance the first time this renders
    storeRef.current = makeStore()
  }

  // Return the Provider component to fetch the store from
  return (
    <Provider store={storeRef.current}>
      {children}
    </Provider>
  );
}