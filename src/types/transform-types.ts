import { RecordMap, TypedValue } from "@/types/shared-types";

// Defines a type for storing transform operation details
interface TransformData {
  parent: string,
  ttype: string,
  parameters: RecordMap<TypedValue>,
};

// Defines a type for storing transform data in the transforms lists
interface Transform extends TransformData {
  id: string,
  index: number,
};

// Exports all transform types
export type { TransformData, Transform };