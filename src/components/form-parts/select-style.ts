// Define the style to apply for the React-Select dropdown
const customSelectStyle = {
  // Changes the style of the menu holding the select options
  menu: (base: any, _state: any) => ({
    ...base,
    backgroundColor: "var(--bs-body-bg)",
    color: "var(--bs-body-color)",
    border: "var(--bs-border-width) solid var(--bs-border-color)",
  }),
  menuList: (base: any, _state: any) => ({
    ...base,
    maxHeight: "200px",
    maxWidth: "100%",
  }),
  // Changes the style of the control box where the user interacts with the select dropdown
  control: (base: any, state: any) => ({
    ...base,
    backgroundColor: "var(--bs-body-bg)",
    color: "var(--bs-body-color)",
    padding: ".0rem .125rem .0rem .125rem",
    transition: "none",
    borderRadius: "var(--bs-border-radius)",
    borderWidth: "var(--bs-border-width)",
    borderStyle: "solid",
    borderColor: state.isFocused ? "#86b7fe" : "var(--bs-border-color)",
    boxShadow: state.isFocused ? "0 0 0 .25rem #0d6efd40" : "0",
  }),
  // Changes the style of the placeholder text
  placeholder: (base: any, _state: any) => ({
    ...base,
    color: "var(--bs-body-color)",
  }),
  // Changes the style of the inner input text
  input: (base: any, _state: any) => ({
    ...base,
    color: "var(--bs-body-color)",
  }),
  // Changes the style of the selected option text
  singleValue: (base: any, _state: any) => ({
    ...base,
    color: "var(--bs-body-color)",
  }),
  // Changes the style of the options in the options menu
  option: (base: any, state: any) => ({
    ...base,
    backgroundColor: state.isFocused ? "light-dark(rgb(118, 118, 118), rgb(195, 195, 195))" : "var(--bs-body-bg)",
    color: state.isFocused ? "light-dark(rgb(255, 255, 255), rgb(16, 16, 16))" : "var(--bs-body-color)",
  }),
  // Changes the style of the dropdown arrow
  dropdownIndicator: (base: any, _state: any) => ({
    ...base,
    color: "light-dark(rgb(80, 80, 80), rgb(200, 200, 200))",
    transition: "none",
  })
};

// Export the custom react-select dropdown style
export default customSelectStyle;