Changelog
=========

Main changes to QC Tools:

Version 4.8.5 (2026-03-01)
--------------------------

- Added support for SSS mosaic name without vessel to Delivery Structure Checks
- Added file-naming check for ISD to Delivery Structure Checks
- Added option to extract CSAR/BAG geotiff to the Input Tab
- Removed beta from HSSD 2026.0
- Disabled splash screen
- Added limited min and max values for Grid QA
- Added checks for very low values for uncertainty and VR uncertainty

Version 4.8.2 (2026-01-13)
--------------------------

- Updated order of Flier Finder execution


Version 4.7.5 (2025-09-03)
--------------------------

- Added HSSD version to Grid Stats plots.
- Added check for folders under Processed for Delivery Structure Checks.
- Improved error message for invalid root folder in Delivery Structure Checks.
- Added file logging in QC4_DEBUG mode.
- Added current HSSD and quality metrics (uncertainty and feature detection) on status bar.
- Added HSSD selector to the HDR tab.
- Fixed bug with NDV for TVU QC in Grid Stats.
- Fixed bug in case of 0 passed nodes in Grid Stats.


Version 4.7.2 (2025-08-27)
--------------------------

- Fixed TVU calculation for IHO Orders.


Version 4.7.1 (2025-08-21)
--------------------------

- Fixed bug in Holiday Finder.


Version 4.7.0 (2025-08-20)
--------------------------

- Experimental release of Grid Stats.
- Changed GUI layout for Grid Stats.
- Added Grid Stats to manual.


Version 4.6.3 (2025-06-24)
--------------------------

- Added debug mode by setting "SSM_DEBUG=1" as environmental variable.
- Fixed bug in counting errors for BAG Checks.
