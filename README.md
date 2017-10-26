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
