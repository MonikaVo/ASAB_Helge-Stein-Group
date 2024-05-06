# ASAB
The framework for the **A**utonomous **S**ynthesis and **A**nalysis of **B**attery
electrolytes comprises software and hardware modules providing capabilities to investigate liquid
electrolytes for batteries.
The hardware setup is located at the Helmholtz Institute Ulm (HIU) in Ulm, Germany.
The software in this repository was developed by employees of
[Karlsruhe Institute of Technology (KIT)](https://www.kit.edu/english/index.php) at the
[Helmholtz Institute Ulm (HIU)](https://hiu-batteries.de/en/).
This repository provides the software to operate the system in an automated mode.

The procedure to install and use the package is described in the following.

# Requirements
Since the software allows to operate several commercially available hardware components,
it requires the respective Software Development Kits (SDKs) of the manufacturers to be
available on the system additional to the Python packages imported in the software
modules.

The SDKs required are the following
- _QmixSDK_

    The SDK associated with the Cetoni Device constituting the formulation unit
    of the ASAB hardware setup. This SDK is commercially available from Cetoni GmbH,
    Korbussen, Germany. Details can be found on their website
    [https://cetoni.de/downloads/manuals/CETONI_SDK/QmixSDK_Python.html](https://cetoni.de/downloads/manuals/CETONI_SDK/QmixSDK_Python.html).
    For generating the required configuration files, the manufacturer's software to
    operate the devices is required.

- _PalmSensSDK_

    This SDK provides an Application Programming Interface (API) for the PalmSens4
    potentiostat. It is available on the PalmSens website
    [https://www.palmsens.com/knowledgebase-article/palmsens-sdk-for-python/](https://www.palmsens.com/knowledgebase-article/palmsens-sdk-for-python/).

For all devices, the commercially available software provided by the device manufacturers
proved valuable in troubleshooting and is mostly a prerequisite to properly set-up and
operate the devices prior to connecting them to ASAB.

# Installation

To install the package, please follow the steps below.

1. Clone this repository.
1. Switch to the directory, to which you cloned the repository and run the command `pip install .`

If you installed all the required SDKs and the respective hardware, you are now ready
to use the ASAB package.


# Usage

## Configuration

ASAB is configurable to meet your specific hardware and software setup. The package
enables a configuration on two levels.

### General configuration
Let us start configuring the package in your environment. For this, we use the
configuration file `src\ASAB\configuration\config.py`. It provides very general
configurations required for the software to resolve its basic dependencies for the
QmixSDK required for the formulation unit.
Please make sure, that the configuration correctly reflects the relative paths to your
QmixSDK.

### Setup of an experiment
To setup an experiment, further configuration is required, which is more specific for
the used hardware and the planned experiment. The following steps guide you through the
process of setting up a new experiment.

1. Create a directory, which you want to use as a root for your new study to store
result etc. In the following, we will reference to this directory as the
_experimentFolder_.
1. It is recommended to additionally create a subdirectory of your _experimentFolder_,
in which you collect all the files you provide prior to starting an experiment to
facilitate separating your inputs form the generated outputs. This subdirectory, could
be called _inputs_.
1. Copy the file `src\ASAB\example_experiment\inputs\experiment_config_template.py` to
your `experimentFolder\inputs\` directory.
1. replace the default values by the values valid for your actual setup, if necessary.
If you follow the above steps regarding the structure of the _experimentFolder_, the
default value for the _experimentFolder_ path should work. The _projectFolder_ and
_experimentFolder_ may be used as origins for relative paths facilitating the
configuration of the setup.
1. Once all the other configurations are done, you can choose, if the balance
functionalities and the Arduino functions shall be simulated or executed on the hardware
by setting the `simulationBalance` and `simulationArduino` flags accordingly
(`True`: simulate, `False`: run on hardware).
1. Place an `edges.csv`, `nodes.csv`, and `tubing.csv` in your `experimentFolder\inputs\`
directory. Examples of the files can be found in the directory `src\ASAB\hardware`.
These files represent the hardware setup you are using. Their content is shortly
described in the following:
    - `nodes.csv`  
        specifie all the nodes available in the setup. A node is any point, to which an
        edge may be connected.
        The meaning of the file's column names is summarized in the following:   
            - _node_: A name for the node, which needs to be unique within your setup.  
            - _position_node_: The coordinates of the position of the node. This is only
            relevant when graphically displaying the graph representing the setup. 
    - `edges.csv`  
        defines all the edges available. The `edges.csv` may contain all tubings and
        connections available, even if they are not used within your current setup.
        Like this, you may use a single `edges.csv` for several setups.
        The meaning of the file's column names is summarized in the following:   
            - _flexibility_: It reports, if an edge is _fixed_ meaning it is located
            within a component like a union and therefore connects two specific nodes,
            or _available_ meaning it is a tubing, which can be used to connect selected
            nodes.  
            - _edge_: The label of the edge. This label must be unique within your
            `edges.csv`.
            - _start_ and _end_: Specifying the start and end node of fixed edges or
            _not_fixed_ for available edges.
            - _ends_: A pair of letters specifying the type of the ends. _X_ unknown,
            _F_ flange, _N_ nut, _C_ cut, and _T_ thickened to reach a larger outer
            diameter.  
            - _length_: The length of the edge in mm.  
            - _diameter_: The innder diameter of the edge in mm.  
            - _dead_volume_: The inner volume of the edge in mL.  
            - _restriction_: Reports, whether the edge is _directed_ or _undirected_.
            Undirected edges are added to the graph twice, once in the direction
            start -> end  and once end -> start.  
            - _status_: Reporting the status of the edge, which is not yet implemented
            and should therefore be set to _empty_ for all edges.
    - `tubing.csv`  
        defines all the non-fixed edges used in the setup. This file contains only
        connections actually present in the setup. The three columns specify the name
        of the start node in the column _start_, the name of the connecting edge in the
        column _edge_, and the name of the end node in the column _end_. Undirected
        edges will be automatically added in both directions, so they must only be
        listed once in the `tubing.csv`.
1. Add a `chemicals.csv` file to your `experimentFolder\inputs\` directory containing
the following columns and one row per chemical used in the experiment:
    - _InChIKey_: The InChIKey related to the respective chemical.
    - _name_: A human-readable name to identify the chemical.
    - _SMILES_: The Simplified Molecular Input Line Specification (SMILES) of the chemical.
    - _molar_mass_: The molar mass of the chemical in g mol<sup>-1</sup>.  
    - _molar_mass_uncertainty_: The uncertainty of the molar mass of the chemical in
    g mol<sup>-1</sup>.  
    - _density_: The density of the chemical in g cm<sup>-3</sup>.  
    - _density_uncertainty_: The uncertainty density of the chemical in g cm<sup>-3</sup>.  
    - _density_temperature_: The temperature corresponding to the reported density in K.  
    - _batch_: The batch number associated with the chemical.  
    - _manufacturer_: The name of the manufacturer of the chemical.  
    - _manufacturing_date_: The date of manufacturing of the chemical.  
    - _references_: References, e.g. if literature values are used.
1. Add a `stockSolutions.csv` file to your `experimentFolder\inputs\` directory
containing the following columns and one row per chemical used in the experiment:
    - _name_: A human-readable name of the stock solution.  
    - _ID_: A unique ID for the stock solution.  
    - _reservoir_: The reservoir from where ASAB can aspirate this stock solution.  
    - _pump_: The pump connected to the respective reservoir.  
    - _mass_total_: The total mass of the supplied stock solution in g.  
    - _mass_total_uncertainty_: The uncertainty of the total mass in g.  
    - _density_: The density of the stock solution in g cm<sup>-3</sup>.  
    - _density_uncertainty_: The uncertainty of the density of the stock solution in
    g cm<sup>-3</sup>  
    - _density_temperature_: The temperature corresponding to the reported density in K.  
    - _\<InChIKey first component\>_: The mass of the first component in the stock
    solution in g. Analogously for all the other components. 
    - _\<InChIKey first component\>\_uncertainty_: The uncertainty of the mass of the
    first component in the stock solution in g. Analogously for all the other components.   
    - _batch_: The batch number associated with the stock solution.  
    - _manufacturer_: The name of the manufacturer of the stock solution.
    (Mainly relevant, if commercial solutions are used.)  
    - _manufacturing_date_: The date of manufacturing of the stock solution.
    - _references_: References, e.g. if literature values are used. 

After completing the configuration files, you are ready to start setting up your
experiment script.

## Basic usage

For running an experiment or a set of experiments, you should implement the procedure in
a script, which will subsequently be executed to run the experiments. An example of a
basic experiment script is shown in
`src\ASAB\example_experiment\inputs\example_experiment.py`.

In the default configuration, ASAB will create a _runFolder_ upon each execution of the
experiment script. In this _runFolder_ all results will be stored in a subfolder called
_Runs_. Further, all the files generated by ASAB during the run and a logfile will be
saved in the _runFolder_.

# Acknowledgements

This project received funding from the European Union’s
[Horizon 2020 research and innovation programme](https://ec.europa.eu/programmes/horizon2020/en)
under grant agreement [No 957189](https://cordis.europa.eu/project/id/957189) (BIG-MAP).
The authors acknowledge BATTERY2030PLUS, funded by the European Union’s Horizon 2020
research and innovation program under grant agreement no. 957213.
This work contributes to the research performed at CELEST (Center for Electrochemical
Energy Storage Ulm-Karlsruhe) and was co-funded by the German Research Foundation
(DFG) under Project ID 390874152 (POLiS Cluster of Excellence).
MV acknowledges the contributions by [lisa-schroeder](https://github.com/lisa-schroeder)
and [Bojing4313](https://github.com/Bojing4313), fruitful discussions with
[fuzhanrahmanian](https://github.com/fuzhanrahmanian) and
[darthlegit](https://github.com/darthlegit) and the valuable input by
[helgestein](https://github.com/helgestein).
