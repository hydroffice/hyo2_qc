.. _survey-bag-checks:

BAG Checks
----------

.. index::
    single: bag checks

How To Use?
^^^^^^^^^^^    
    
Evaluates BAGs to ensure compliance with NOAA NBS and BAG specification requirements.

In order to access this tool, load in a BAG file into the **Data Inputs** tab.

* Select the **BAG Checks** tab (:numref:`fig_bag_checks`) on the bottom of the QC Tools interface.

* Check the boxes that correspond with the checks you wish to perform.

* In **Execution**, click **BAG Checks v2**.

.. _fig_bag_checks:
.. figure:: _static/bag_checks_interface.png
    :width: 700px
    :align: center
    :alt: fliers tab
    :figclass: align-center

    The **BAG Checks** tab.

|

-----------------------------------------------------------

|

How Does It Work?
^^^^^^^^^^^^^^^^^

The BAG files are inspected to ensure compliance with NOAA NBS requirements and BAG Format Specification Documents:

* **Check the overall structure**: Check that the critical components of BAG structure are present.
   * BAG Root group
   * BAG Version attribute
   * Metadata dataset
   * Elevation dataset
   * Uncertainty dataset
   * Tracking List dataset
   * For VR Surfaces:
      * VR Metadata dataset
      * VR Refinements dataset
      * VR Tracking List dataset

* **Check the metadata content**: Checks to ensure that metadata associated with the BAG are appropriately attributed:
   * Metadata dataset
   * VR Metadata dataset (VR only)
   * For NOAA NBS Profile:
      * Resolution matches with filename (SR only).
      * Spatial reference system is projected.
      * Vertical datum is defined.
      * Creation date.
      * Survey start date.
      * Survey end date.
      * Product Uncertainty.

* **Check the elevation layer**: Checks to ensure the validity of the elevation layer of BAG. Checks the following:
   * For the presence of a Elevation dataset.
   * All depth values are not NaN.
   * VR Refinements (VR only).

* **Check the uncertainty layer**: Checks to ensure the validity of the uncertainty layer in the BAG. Checks the following:
   * For the presence of an Uncertainty dataset.
   * All values are not NaN.
   * Uncertainty values are only positive.
   * VR Refinements (VR only).
   * For NOAA NBS Profile:
      * Uncertainty values are not too high:
         * The uncertainty threshold is based on the max depth: :math:`UT = 4.0m + 0.1 * d _{max}`.
         * This check is skipped in case of ellipsoid depths (detected from the filename).

* **Check the tracking list**: Checks to ensure the validity of the tracking list. Checks the following:
   * For the presence of the Tracking List dataset and the VR Tracking List dataset (VR only).
   * Validity of the entries in the 'row' column.
   * Validity of the entries in the 'col' column.

* **Check GDAL Compatibility**: Checks to ensure that the surface is compatible with GDAL. Checks the following:
   * Checks that that the grid does not have more than 10,000,000 refinement grids which will result in a GDAL error.

|

-----------------------------------------------------------

|

What do you get?
^^^^^^^^^^^^^^^^^

Upon completion of the execution of **BAG Checks** you will receive a pop-up verification "pass" if your surface passes all the checks, or "fail" if your surface fails any one check (:numref:`fig_bag_checks_output`).

.. _fig_bag_checks_output:
.. figure:: _static/bag_checks_output.png
    :width: 450px
    :align: center
    :alt: fliers tab
    :figclass: align-center

    The **BAG Checks** pop-up output.

**BAG Checks** produces a PDF report that indicates what checks were performed and the results of the checks (:numref:`fig_bag_checks_results`). At the end of the report a summary indicates how many warnings and errors were identified for the surface (:numref:`fig_bag_checks_summary`).

.. _fig_bag_checks_results:
.. figure:: _static/bag_checks_results.png
    :width: 400px
    :align: center
    :alt: fliers tab
    :figclass: align-center

    An example of a **BAG Checks** PDF report.

.. _fig_bag_checks_summary:
.. figure:: _static/bag_checks_summary.png
    :width: 300px
    :align: center
    :alt: fliers tab
    :figclass: align-center

    An example of the **BAG Checks** summary.
	
The naming convention of the output files contains important information about BAG Checks.
Each piece of information is separated by a period in the naming convention. See :numref:`fig_bag_checks_convention`.

.. _fig_bag_checks_convention:
.. figure:: _static/bag_checks_convention.png
    :width: 800px
    :align: center
    :alt: naming convention of output file for bag checks
    :figclass: align-center

    Example naming convention for a BAG Checks output.
