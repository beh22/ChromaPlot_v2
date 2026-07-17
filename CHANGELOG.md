# Changelog

## Version 2.1.0 - 2026-XX-XX

### Added
- Added configurable fraction labels for imported datasets, including sequential numbering, filtering options, and custom line and text styling
- Added shaded regions linked to individual curves, with support for volume ranges, fraction ranges, and interactive click-drag selection
- Added a Shading tab for viewing, editing, hiding, and removing shaded regions across the project
- Added project-wide controls to show or hide all curves
- Added persistent window positioning for fraction and shaded-region dialogs

### Changed
- Updated the Curve tab to display the parent dataset name
- Updated the Dataset tab so it remains populated when a curve within that dataset is selected
- Improved tick-spacing controls with safer minimum spacing and Auto reset buttons
- Updated automatic curve styling so curves are coloured by dataset rather than curve type, with line styles used to distinguish different curve types

### Fixed
- Prevented excessive tick generation from very small manual tick-spacing values
- Fixed the syncing between the visible curve checkboxes in the Dataset tree and Curve tab


## Version 2.0.2 - 2026-05-26

### Changed
- Changed update dialog text to include `pipx` upgrade instructions
- Improved update dialog on Windows


## Version 2.0.1 - 2026-05-22

### Changed
- Fixed update checker on Windows
- Fixed fonts for Windows compatability
- Improved dialog sizes for Windows compatability


## Version 2.0.0 - 2026-05-21

### Added
- Complete rewrite of ChromaPlot from the ground up
- Project-based workflow with save/load support
- Multi-dataset overlay plotting
- Customisable curve styling
- Dataset management panel
- Curve visibility controls
- Dockable interface layout
- Improved export handling
- Welcome dialog and startup workflow
- Modernised plotting architecture

### Changed
- Replaced the separate “Single” and “Overlay” modes from v1 with a unified workflow
- Redesigned GUI and internal project structure
- Improved dataset importing and metadata handling
