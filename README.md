# Energy-Market-Tools

This repository contains a collection of tools developed to assess the value proposition and potential market for distributed generation technology in residential, commercial and industrial markets in the United States.

It uses the DOE EIA API to download state level rate and consumption data, and then uses this data to estimate the potential state-level markets for distibuted generation technology given the performance, cost and utilization characteristics of such systems.

## EIA Data Queries

EIADataQuery.py (and EIADataQuery_pd.py)d is a collection of Python 3.6 classes that were developed 
to download data from the U.S. Department of Energy's Energy Information 
Administration (EIA) using their data API.  

The API is described at the link that follows--
https://www.eia.gov/opendata/

Registration is required in order to obtain a key that must be 
included in each query. The key is currently saved in the variable
_EIA_RegKey in the EIAQuery class.

This module contains two main classes that are intended to provide easy data 
access and subsequent processing.

  1) EIAQuery:        A low-level data query that downloads and 
                      stores the specified data.

  2) EIAStateQuery:   A state-level query that downloads a specified 
                      set of quiries for the specified sector (COMmercial,
                      INDustrial, or RESidential) and state (e.g. CT, NY)
                      The data include for time span available in the
                      repository--annual average electric and natural gas 
                      rates and the total annual electricity usage.

## Distributed Generation Value Proposition

DGValueProp.py is a collection of classes that are desgined to assess the value proposition for distributed generation (DG)
technology in the United States--at the state (e.g. Connecticut) and sector (e.g. Commercial) level of analysis.
The following classes are defined within it--
1.  DGOut
2.  DGIn
3.  DGValProp
4.  SensitivityStudy
5.  EPA_CHP_System_Specs
DGOut is a class that is designed to store distirbuted generation value proposition metrics (e.g NPV, IRR, etc.), a market
penetration estimate, and the effective electric efficiency.  Its only method is __init__.
DGIn is a class that is designed to store the necessary input parameters for the assessment of the value proposition for DG
equipment.  These parameters include a number of efficiency, cost and utilization metrics.
DGValProp is a class that contains the the input assumptions and output economic value proposition estimate for a 
specific distributed generation scenario.  It consists of two sub-classes:  DGin() and DGOut().
SensitivityStudy is a class designed to run and store a two-parameter DG value proposition sensitivity study for a specific 
region (e.g. state, US), year, and sector (e.g. COM).  In a study, DG system input characteristics are varied over the 
specified range while holding the remainder at constant/nominal values.
The "input" parameters/attributes include:
    1. Region - A string containing a two letter region code 
        (typically a state abbreviation).  The default is "US"--the entire
        United States.
    2. Year - A integer containing a four digit year.  The default is 
        2015.
    3. Sector - A specification for the market sectors (e.g. Commercial,
        Residential, or Industrial).  Only the first letter (e.g. C, R, I)
        is significant.
    4.  
The "output" attribute is an instance of class DGValProp().
Several methods are provided to facilitate visualization of the output. These
methods include--
    1. x_plot - 
    2. contour_plot - 
    
EPA_CHP_System_Specs is a class that contains existing EPA CHP System Specifications from -- 
https://www.epa.gov/sites/production/files/2015-07/documents/catalog_of_chp_technologies.pdf.
