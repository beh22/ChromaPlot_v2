# ChromaPlot v2 TODO

- fix 'visible' button in curve tab to sync with box in dataset tree
- if a curve is selected and then the dataset button is clicked, the dataset that the curve is in should be selected
- fix dataset tree refresh, re-expands

- include dataset name on plot tab
- have hide all curves (for all datasets) button
- preserve tree expand state in datasets/curve and shading
- different colours for uv traces from multiple curves

## GUI and UX Improvements

### Welcome Dialog
- Add About dialog
- Improve styling/theme consistency
- Add links/documentation/help access

### Main Window
- Decide whether settings panel should become a separate floating dialog instead of a dock widget
- Save and restore window geometry/layout in project files
- Decide whether window/layout changes should mark project as dirty
- Improve stylesheet/theme across the application
- Add Help menu/documentation access

### Dataset Management
- Warning when attempting to load duplicate datasets
  - Example:
    - “Dataset 'X' appears to already be loaded. Load again?”
- Apply transforms to all curves in a dataset


## Plotting Features

### Annotations and Regions
- Vertical marker
- Text annotations

### Axes and Layout
- Optional secondary axis
- Improve figure size handling
  - Export using current visible plot size
  - Clarify interaction between preview size and export size


## Analysis Features

- Peak/integration tools
- Other chromatography analysis utilities, depending on data type


## Data Import and Compatibility

### Additional Data Types
- Add support for non-AKTA datasets
  - FIDA
  - LC-MS
  - SEC-MALS
  - Generic CSV input

## Packaging and Distribution

- Sort packaging for desktop app

## Long-Term Ideas

- Recent projects list
- Custom themes/light mode
- Multi-panel figures/layouts