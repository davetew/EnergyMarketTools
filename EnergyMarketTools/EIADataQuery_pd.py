"""
Created on Fri Apr 21 11:57:23 2017

    EIADataQuery.py is a collection of Python 3.6 classes that were developed 
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
                            
@author: David.Tew
"""
import numpy as  np
import requests as rq
import pandas as pd
import pint

# Initialize a pint Unit Registry
ureg = pint.UnitRegistry()
Q_ = ureg.Quantity

#from pathlib import Path
#import pickle

class EIAQuery():
    """Low-level EIA data query.  Load specified EIA data query."""
    
    # EIA API Registration Key
    _EIA_RegKey = 'e28c81f13500f013f8ef67e3a3e4ed9d'
    _QueryPrefix = 'http://api.eia.gov/series/?api_key=%s&series_id=' % (_EIA_RegKey)
    
    def __init__(self,DataSets,GetFromEIA=False):
        """Initialize an instance of EIA Query given a specified DataSet or list of DataSet"""

        if isinstance(DataSets, str):
            # Convert DataSet to a list with one item
            DataSets = [DataSets]

        """Get the data from the EIA if told to do so, or the data file isn't
        at the specified location."""
        
        DataFrameList = []
        for DataSet in DataSets:

            # Full data query
            FullQuery = self._QueryPrefix + DataSet
        
            # Execute data query & save the data in a dictionary with the below keys of interest
            #   name: a string containing the dataset name
            #   geography: a string containing the state/region for the data (optional)
            #   units: a string containing units for the quantitative data
            #   data: a N x 2 array with the period in the first column and the data in the second
            print('Downloading ' + DataSet + ' from the EIA.')
            RawData = rq.get(self.FullQuery).json()['series'][0]

            # Save the data in a more concise form
            for key in ['name', 'geography', 'units', 'data']:
                eval(f"{key} = RawData.get({key})")
            
            # Convert the data list of lists to a numpy array
            data = np.array(data)
            
            # Save the data in a more convenient form
            Period, Value = data[:, 0], data[:, 1]  

            # Store quantitative data in dictionary {period: value}
            DataDict = {period: Q_(value if value is not None else np.nan, units) for period, value in zip(Period, Value)}

            # Create a dataframe and add it to the list of dataframes
            DataFrameList.append(pd.DataFrame.from_dict(DataDict, orient='index', columns=[name]))

        # Merge the list of dataframes into a single dataframe with 

    @property
    def TimeSpan(self):
        """Save the intial and final year of the data set in a range object."""
        Years = np.asarray(list(self.QuantData.keys())).astype(int)
        return range(Years.min(),Years.max())
    
    @property
    def Years(self):
        return np.asarray(sorted(list(self.QuantData.keys())))
    
    @property
    def Values(self):
        return np.asarray([self.QuantData[year] for year in self.Years])

    def _StandardizeUnits(self):
        
        # Conversion Factors & New Units
        Conversions = {'Dollars per million Btu': (1/293.3,'$/kWh'),
                       'Dollars per Thousand Cubic Feet': (1.025/293.3, '$/kWh'),  # Assume conversion is for NG
                       'Million kilowatthours': (1e6,'kWh'),
                       'thousand megawatthours': (1e6, 'kWh'),                          
                       'kWh': (1, 'kWh'),                         
                       'Dollar per kilowatthour': (1,'$/kWh'),
                       '$/kWh': (1, '$/kWh'), 
                       'Trillion Btu': ( 0.29307 ,'TWh') }                            
 #                      'cents per kilowatthour': (0.01,'$/kWh') }                          }                         
                                    
        for key, value in self.QuantData.items():
            self.QuantData[key] *= Conversions[self.Units][0] 
        
        self.Units = Conversions[self.Units][1]
        
        return self

             
class EIAStateQuery():
    """State level data query. Upon initialization load annual average 
    electricity & natural gas rates and annual generation for the specified 
    sector (e.g. RES, COM or IND) and region from the EIA for all available years.
    
    The input parameters include the--
        1. Region - A string containing a two letter region code 
            (typically a state abbreviation).  The default is "US"--the entire
            United States.
        2. Sector - A specification for the market sectors (e.g. Commercial,
            Residential, or Industrial).  Only the first letter (e.g. C, R, I)
            is significant.
            
    The downloaded data is stored in 
        1. Data - A dictionary of instances of EIADataSet() that is organized 
            by year (an integer)."""   
    def __init__(self,Region='US',Sector='COM'):
        
        # Save region & sector specifications
        self.Region = Region
        self.Sector = Sector
                
        DataSets = {"Elec_Rate": "SEDS.ES%sCD.%s.A" % (Sector[0], Region),
                    "NG_Rate":  "SEDS.NG%sCD.%s.A" % (Sector[0], Region),
                    "Elec_Consumption": "SEDS.ES%sCP.%s.A" % (Sector[0], Region)}

        Queries = list(DataSets.keys())
        QueryData = dict()
        InitYear = 2100; FinalYear = 1900
        for i, Query in enumerate(Queries):
            QueryData[Query] = EIAQuery(DataSets[Query])
            InitYear = np.min((InitYear,QueryData[Query].TimeSpan.start))
            FinalYear = np.max((InitYear,QueryData[Query].TimeSpan.stop))
            
        #self.QueryData = QueryData
            
        self.Data = {year: EIAStateDataSet( elec_rate_dol_kWh=QueryData['Elec_Rate'].QuantData.get(year,float("NaN")),
                  ng_rate_dol_kWh = QueryData['NG_Rate'].QuantData.get(year,float("NaN")),
                  net_generation_kWh = QueryData['Elec_Consumption'].QuantData.get(year,float("NaN")) ) 
                  for year in range(InitYear,FinalYear+1)}
                
        # Create panda's data frame version of state data
        index = [year for year in range(InitYear,FinalYear+1) ]
        data = { 'Elec_Rate_dol_kWh':  [ QueryData['Elec_Rate'].QuantData.get(year,float("NaN")) for year in range(InitYear,FinalYear+1)],
                 'NG_Rate_dol_kWh': [ QueryData['NG_Rate'].QuantData.get(year,float("NaN")) for year in range(InitYear,FinalYear+1)],
                 'Elec_Consumption_kWh': [ QueryData['Elec_Consumption'].QuantData.get(year,float("NaN")) for year in range(InitYear,FinalYear+1)]} 

        self.DataFrame = pd.DataFrame( data = data, index = index )
            
# State-level EIA data class
class EIAStateDataSet:
    """Class intended for the storage of rate and energy usage data for
    a specified region, year, and sector.  Each attribute is a float
    that has a default value of NaN.  
    
    The attributes include--
        ng_rate_dol_kWh - The period average natural gas rate in $/kWh on 
            an LHV-basis.
        elec_rate_dol_kWh - The period average electric rate in $/kWh.
        net_generation_kWh - The net generated electricity in kWh.
        """
    def __init__(self, elec_rate_dol_kWh=float("NaN"),
                 ng_rate_dol_kWh=float("NaN"),
                 net_generation_kWh=float("NaN")):
        self.elec_rate_dol_kWh = elec_rate_dol_kWh
        self.ng_rate_dol_kWh = ng_rate_dol_kWh
        self.net_generation_kWh = net_generation_kWh 
        
        
