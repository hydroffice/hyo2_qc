Overview
--------

.. index::
    single: survey review

The **Survey Review** tab will:

* Ingests bathymetric grids and feature files (see :ref:`survey-data-inputs`).

* Scan grids for anomalous grid data ":index:`fliers`" (see :ref:`survey-detect-fliers`).

* Scan grids for empty grid nodes that meet NOAA NOS Hydrographic Survey Specifications and Deliverables (`HSSD`_) definitions of ":index:`holidays`" (see :ref:`survey-detect-holidays`).

* Compute basic grid statistics to ensure compliance to uncertainty and density requirements (see :ref:`survey-grid-qa`).

* Scan grids to ensure the eligibility of soundings :index:`designated` (see :ref:`survey-scan-designated-label`).

* Scan features to ensure proper attribution (see :ref:`survey-scan-features`).

* Ensure surveyed features are properly accounted for in the :index:`gridded bathymetry` (see :ref:`survey-valsou-checks`).

* Export :index:`bottom samples` to a text file for archival (see :ref:`survey-sbdare-export`).

* Ensures the required directory structure and completeness of survey deliverables (see :ref:`survey-submission-checks`).

.. _HSSD: https://nauticalcharts.noaa.gov/hsd/specs/HSSD_2017.pdf
