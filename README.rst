yaml2ncml
=========

NcML aggregation from YAML specifications.

``yaml2ncml`` is a command line tool to facilitate the creation of
`NcML
aggregation <https://www.unidata.ucar.edu/software/thredds/current/netcdf-java/ncml/Aggregation.html>`__
file for THREDDS servers.

Install it using pip or conda.

.. code:: bash

    pip install yaml2ncml
    # or
    conda install -c https://conda.binstar.org/ioos yaml2ncml

The user must create a YAML config file (see the example below) and run:

.. code:: bash

    yaml2ncml roms.yaml

    # or save the output

    yaml2ncml roms.yaml --output roms_aggregation.ncml

roms.yaml
---------

.. code:: yaml

    dataset:
        id: "USGS_COAWST_MVCO_CBLAST_Ripples_SWAN_40m"

        title: "USGS-CMG-COAWST Model: CBLAST2007 Ripples with SWAN-40m res"

        summary: "Simulation of hydrodynamics and bottom stress south of Marthas Vineyard, MA using the COAWST modeling system.  These results are from the 40m inner nest of a four-level nested simulation."
        
        project:
            - CMG_Portal
            - Sandy_Portal

        creator:
            email: nganju@usgs.gov
            name: Neil Ganju
            url: http://water.usgs.gov/fluxes

        publisher:
            email: tkalra@usgs.gov
            name: Tarandeep Kalra
            url: http://www.usgs.gov

        contributor:
            role: advisor
            email: rsignell@usgs.gov
            name: Rich Signell
            url: http://profile.usgs.gov/rsignell


        license: "The data may be used and redistributed for free but is not intended for legal use, since it may contain inaccuracies. Neither the data Contributor, nor the United States Government, nor any of their employees or contractors, makes any warranty, express or implied, including warranties of merchantability and fitness for a particular purpose, or assumes any legal liability for the accuracy, completeness, or usefulness, of this information."

        references:
            - http://www.whoi.edu/science/AOPE/dept/CBLASTmain.html
            - http://water.usgs.gov/fluxes/mvco.html
            - doi:10.1029/2011JC007035

        acknowledgements:
            - USGS-CMGP
            - NSF

    variables:
        include:
            - temp
            - salt

        exclude:
            - ubar
            - vbar

    aggregation:
        time_var: ocean_time
        dir: Output
        sample_file: test_nc4_0001.nc
        pattern: .*test_nc4_[0-9]{4}\.nc$


Notes on the YAML file: 

1. The aggregation `dir:` is the directory where the data (e.g. NetCDF files) are located, relative to the directory where the NcML will be.  In the above example, the NetCDF files are located in a subdirectory called "Output".  If the NetCDF files will be in the same directory as the NcML file, specify `dir: '.'`. 

2. Specify that all variables should appear in the aggregation (none excluded) like this:

.. code:: yaml

    variables:
        include:
            - All

        exclude:
            - None
