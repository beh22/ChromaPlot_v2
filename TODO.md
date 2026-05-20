# ChromaPlot v2 TODO

## High Priority

### Documentation and Release Preparation

-   Update ChromaPlot v1 README to point users to v2
-   Finalise packaging and installation workflow
-   Create first GitHub release (`v2.0.0`)

### Packaging and Distribution
-   Ensure app runs cleanly from source
-   Finalise `pyproject.toml`
-   Add `.gitignore`
-   Test installation in clean environment
-   Later: packaged desktop app builds


## GUI and UX Improvements

### Welcome Dialog
-   Add About dialog
-   Improve styling/theme consistency
-   Add links/documentation/help access

### Main Window
-   Decide whether settings panel should become a separate floating dialog instead of a dock widget
-   Save and restore window geometry/layout in project files
-   Decide whether window/layout changes should mark project as dirty
-   Improve stylesheet/theme across the application
-   Add Help menu/documentation access

### Dataset Management
-   Warning when attempting to load duplicate datasets
  - Example:
    - “Dataset 'X' appears to already be loaded. Load again?”
-   Apply transforms to all curves in a dataset


## Plotting Features

### Annotations and Regions
-   Fraction number display
  -   Customise appearance
  -   Toggle visibility
-   Shaded regions
  -   Define by fraction numbers
  -   Define by volume range
  -   Editable/removable region list
-   Vertical marker
-   Text annotations

### Axes and Layout
-   Optional secondary axis
-   Improve figure size handling
  -   Export using current visible plot size
  -   Clarify interaction between preview size and export size



## Analysis Features

-   Peak/integration tools
-   Additional analytical overlays
-   Other chromatography analysis utilities


## Data Import and Compatibility

### Additional Data Types
-   Add support for non-AKTA datasets
  -   FIDA
  -   LC-MS
  -   SEC-MALS
  -   Generic CSV input



## Project and File Management

-   Update checker
  -   Compare installed version with latest GitHub version
  -   Notify users about available updates



## Long-Term Ideas

-   Recent projects list
-   Custom themes/light mode
-   Multi-panel figures/layouts