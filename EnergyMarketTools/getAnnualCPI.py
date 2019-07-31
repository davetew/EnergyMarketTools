import pandas as pd

# Import the Fred API from the St. Louis Federal Reserve Bank
from fredapi import Fred
fred = Fred(api_key='74dc0c0ba5a6d1d5c0e3704cee396565')

def getAnnualCPI(SeriesNames=['CPALTT01USA661S', 'USACPICORAINMEI'], 
                 SeriesLabels=['All Items', 'No Food or Energy'],
                 displayData=False, plotData=False):
  """Get and return a dataframe with US Annual CPIs and their associated labels"""
  
  # Get the CPI data from Fred and store it in a dictionary using the labes as keys
  cpi = {}
  for Name, Label in zip(SeriesNames, SeriesLabels):
    cpi[Label] = fred.get_series(Name)
    cpi[Label].index = cpi[Label].index.map(lambda x: x.year)

  # Create a dataframe with all the data
  cpi_df = pd.DataFrame.from_dict(cpi).dropna()

  # Normalized the index (i.e. divide by 100)
  cpi_df = cpi_df.apply(lambda x: x/100)

  if displayData: display(cpi_df)
  if plotData: cpi_df.plot(grid=True, title='US CPI')

  return cpi_df
