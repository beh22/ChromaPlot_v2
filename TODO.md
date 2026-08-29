# ChromaPlot v2 TODO

## GUI and UX Improvements

### Welcome Dialog
- Add About dialog
- Improve styling/theme consistency
- Add links/documentation/help access

### Main Window
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
  - Right click on plot for menu to turn on vertical marker
  - Also appears in 'view' menu with keyboard shortcut
  - Activating it opens a small window which contains the y values at the volume for each curve visible on the plot
  - Can also customise marker appearance (if the user wants to have it present when exporting)
  - Have a box to automatically move the marker to a specific volume
  - Move it around by dragging on the plot? other option is slider on pop out window like in v1

- Text annotations

### Axes and Layout
- Optional secondary axis
  - Have option in 'plot' menu (probs best place) to activate secondary (and tertiary?) axis
  - Can decide what curve type (gradient, conductivity) or pick a specific curve
  - Can customise (probs just limits and tick spacing?) in the same way as the other axes, but this only becomes present when activated


- Improve figure size handling
  - Export using current visible plot size
  - Clarify interaction between preview size and export size


## Analysis Features

- Peak/integration tools
- Automatic peak detection
- Molecular weight determination

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