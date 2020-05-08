.. _survey-grid-qa:

Grid QA
-------

.. index::
    single: grid qa

How To Use?
^^^^^^^^^^^    
    
Computes grid statistics to ensure compliance with uncertainty and density requirements.

* Select the **Grid QA** tab (:numref:`fig_grid_qa`) on the bottom of the QC Tools interface.

.. index::
    single: grid qa; coverage

* Check the boxes that correspond with the plots you wish to generate. 

.. index::
    single: grid, uncertainty, density

* In **Execution**, click **Grid QA v6**.

.. _fig_grid_qa:
.. figure:: _static/grid_qa_interface.png
    :width: 700px
    :align: center
    :alt: fliers tab
    :figclass: align-center

    The **Grid QA** tab.

* After computing, the output window opens automatically, and the results are shown (:numref:`fig_grid_qa_output`).

.. _fig_grid_qa_output:
.. figure:: _static/grid_qa_results.png
    :width: 240px
    :align: center
    :alt: fliers tab
    :figclass: align-center

    The output message at the end of **Grid QA v5** execution.


* From the output window, view each plot to assess the grid compliance to uncertainty and density specifications.

.. note::
    The **Plot depth vs. density** and **Plot depth vs. TVU QC** can potentially require a large amount of memory
    (i.e., when the input grid contains hundreds of millions of nodes). As such, both plots are unflagged by default.
    You can flag them if you need their output. If having both plots selected triggers a memory error,
    you may try to flag these plots once at a time.

|

-----------------------------------------------------------

|

How Does It Work?
^^^^^^^^^^^^^^^^^

The Depth, Uncertainty, Density (if available), and a computed Total Vertical Uncertainty (TVU) QC layer are used to compute particular statistics shown as a series of plots.  

**The following plots are the output of Grid QA:**
    * The Depth layer is plotted as a distribution (plot entitled **"Depth Distribution"**).
    
    * The Density layer is plotted as a distribution (plot entitled **"Object Detection Coverage"**).

        * Percentages of nodes less than 5 soundings per node fall in the red shaded region of the plot and together must be less than 5% of all nodes in order to "pass".
        
    * Density is plotted against the corresponding Depth of the node (plot entitled **"Node Depth vs. Sounding Density"**).
    
    * TVU QC (IHO S-44) is plotted as a distribution (plot entitled **"Uncertainty Standards - NOAA HSSD"**).
    
        * Percentages of nodes with TVU QC greater than 1.0 (indicating that the allowable error has been exceeded) fall in the red shaded region of the plot, and together must be less than 5% of all nodes in order to "pass".
        
    * TVU QC (IHO S-44) is plotted against the corresponding Depth of the node (plot entitled **"Node Depth vs. TVU QC"**).

    * Only for Variable Resolution grids, a histogram with the percentage of nodes at the prescribed resolution is created. This histogram can be used to evaluate whether *"95% of all surface nodes [..] have a resolution equal to or smaller than the coarsest allowable resolution for the node depth"* (NOAA HTD 2017-2 "Caris Variable Resolution Grids").
	
    * *TVU QC (IHO S-57 CATZOC) [Branch]* is plotted as a distribution (plot entitled *"Uncertainty Standards - CATZOC ..."*).

|

**TVU QC Calculations**

The TVU QC layer is calculated on-the-fly by the program. TVU QC based on IHO S-44 Orders 1 and 2 is in alignment with the requirements set forth by the HSSD and is determined by a ratio of uncertainty to allowable error. It is calculated as such:  

.. math::

    TVU\, QC _{(IHO\hspace{1mm} S\textendash 44)} = Uncertainty / \sqrt{A^2 + (B * Depth)^2}

where :math:`A = 0.5, B = 0.013` for Order 1 (depths less than 100 m), and :math:`A = 1.0, B = 0.023` for Order 2 (depths greater than 100 m).


TVU QC based on IHO S-57 CATZOC is used by the hydrographic branch to evaluate the quality of bathymetry for surveys that are not subject to the HSSD. **This check should NOT be used by NOAA field units or contract field units.** For TVU QC based on IHO S-57 CATZOC, TVU QC is calculated as such:

.. math::

    TVU\, QC _{(IHO\hspace{1mm} S\textendash 57\hspace{1mm} CATZOC)} = Uncertainty / (A + (B * Depth))

where for:

    *CATZOC A1:* :math:`A = 0.5, B = 0.01`

    *CATZOC A2 and CATZOC B:* :math:`A = 1.0, B = 0.02`

    *CATZOC C:* :math:`A = 2.0, B = 0.05`


Running the *TVU (IHO S-57 CATZOC) [Branch]* check will generate three plots, one for each calculation of CATZOC TVU QC mentioned above.