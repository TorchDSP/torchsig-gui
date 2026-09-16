// Defines a number comparison function for comparing transform indeces
function numberComparer(a: number, b: number) {
  if (a < b) { return -1; }
  if (a > b) { return 1; }
  return 0;
}

// Defines a function that takes the current sorted ids, a source, and a target, and returns a list of updates
function generateSortUpdates(list: string[], source: number, target: number) {
  // If nothing has moved, return an empty update list
  if (source === target) {
    return [];
  }

  // Create the update list
  const sortUpdates = [];
  for (let i = 0; i < list.length; i++) {
    // Use the current index as the default
    let newIndex = i;

    // If the index is for the source, move it to the target
    if (i === source) {
      newIndex = target;
    }
    // If the source moved up, make any indeces in range move down
    else if (source < i && i <= target) {
      newIndex--;
    }
    // If the source moved down, make any indeces in range move up
    else if (target <= i && i < source) {
      newIndex++;
    }

    // If the new index is not the old one, create an update
    if (newIndex !== i) {
      sortUpdates.push({ id: list[i], changes: { index: newIndex } });
    }
  }

  // Return the new update list
  return sortUpdates;
}

// Exports the transform utility functions
export { numberComparer, generateSortUpdates };