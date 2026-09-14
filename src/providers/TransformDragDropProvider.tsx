"use client"

import { useAppDispatch } from "@/store/hooks";
import { resortTransforms } from "@/features/transform-form/transform-slice";

import { DragDropProvider } from "@dnd-kit/react";
import { isSortable } from "@dnd-kit/react/sortable";
import { RestrictToWindow } from "@dnd-kit/dom/modifiers";
import { RestrictToVerticalAxis } from "@dnd-kit/abstract/modifiers";

// Provides the environment for items within to be draggable and droppable
export default function TransformDragDropProvider({ children }: { children: React.ReactNode }) {
  // Get the store dispatch function
  const dispatch = useAppDispatch();

  // Return the provider component to drag and drop items within
  return (
    <DragDropProvider
      modifiers={
        // Keep all draggable and droppable items on the vertical axis within the provider component
        (defaults) => [...defaults, RestrictToWindow, RestrictToVerticalAxis]
      }
      onDragOver={(event) => {
        // Prevent the default behavior
        event.preventDefault();

        // When a swap is detected, update the transforms lists
        const {source, target} = event.operation;
        if (isSortable(source) && isSortable(target)) {
          dispatch(resortTransforms(source.index, target.index));
        }
      }}
    >
      {children}
    </DragDropProvider>
  );
}