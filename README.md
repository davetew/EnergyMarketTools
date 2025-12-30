# EnergyMarketTools

This repository contains a collection of tools developed to assess the value proposition and potential market for distributed generation technology in residential, commercial and industrial markets in the United States.

It uses the DOE EIA API to download state level rate and consumption data, and the Federal Reserve Economic Data (FRED) API to access Consumer Price Index (CPI) data. The tools use this data to estimate the potential state-level markets for distributed generation technology given the performance, cost and utilization characteristics of such systems.

## Features

- Query and download energy data from the U.S. Department of Energy's Energy Information Administration (EIA) API
- Access Consumer Price Index (CPI) data from the Federal Reserve Economic Data (FRED) API
- Assess distributed generation (DG) value propositions at state and sector levels
- Perform sensitivity studies on DG system parameters
- Visualize market potential and economic metrics for distributed generation technologies
- Support for residential, commercial, and industrial sectors

## Installation

```bash
# Clone the repository
git clone https://github.com/davetew/EnergyMarketTools.git
cd EnergyMarketTools

# Install the package
pip install -e .
```

### Dependencies

The following packages are required:
- numpy
- matplotlib
- pandas
- requests
- fredapi

These dependencies will be automatically installed when you install the package using pip.

## Configuration

### EIA API Key

To use the EIA data query tools, you need to obtain an API key from the U.S. Department of Energy's Energy Information Administration (EIA):

1. Visit [https://www.eia.gov/opendata/](https://www.eia.gov/opendata/)
2. Register to obtain your API key
3. Update the `_EIA_RegKey` variable in the `EIAQuery` class with your key

### FRED API Key

To use the CPI data retrieval functionality, you need a FRED API key from the Federal Reserve Bank of St. Louis:

1. Visit [https://fred.stlouisfed.org/docs/api/api_key.html](https://fred.stlouisfed.org/docs/api/api_key.html)
2. Register to obtain your API key
3. Configure the API key in the `getAnnualCPI.py` module

## Modules

### EIA Data Queries

`EIADataQuery.py` (and `EIADataQuery_pd.py`) - A collection of Python classes developed to download data from the U.S. Department of Energy's Energy Information Administration (EIA) using their data API.

**Main Classes:**

1. **`EIAQuery`**: A low-level data query that downloads and stores the specified data.

2. **`EIAStateQuery`**: A state-level query that downloads a specified set of queries for the specified sector (Commercial, Industrial, or Residential) and state (e.g., CT, NY). The data includes the time span available in the repository—annual average electric and natural gas rates and the total annual electricity usage.

### Distributed Generation Value Proposition

`DGValueProp.py` - A collection of classes designed to assess the value proposition for distributed generation (DG) technology in the United States at the state (e.g., Connecticut) and sector (e.g., Commercial) level of analysis.

**Main Classes:**

1. **`DGOut`**: A class designed to store distributed generation value proposition metrics (e.g., NPV, IRR), a market penetration estimate, and the effective electric efficiency. Its only method is `__init__`.

2. **`DGIn`**: A class designed to store the necessary input parameters for the assessment of the value proposition for DG equipment. These parameters include a number of efficiency, cost, and utilization metrics.

3. **`DGValProp`**: A class that contains the input assumptions and output economic value proposition estimate for a specific distributed generation scenario. It consists of two sub-classes: `DGIn()` and `DGOut()`.

4. **`SensitivityStudy`**: A class designed to run and store a two-parameter DG value proposition sensitivity study for a specific region (e.g., state, US), year, and sector (e.g., COM). In a study, DG system input characteristics are varied over the specified range while holding the remainder at constant/nominal values.

   **Input parameters/attributes:**
   - Region: A string containing a two-letter region code (typically a state abbreviation). Default is "US" (entire United States)
   - Year: An integer containing a four-digit year. Default is 2015
   - Sector: A specification for the market sectors (Commercial, Residential, or Industrial). Only the first letter (C, R, I) is significant

   **Visualization methods:**
   - `x_plot`: Generate line plots for sensitivity analysis
   - `contour_plot`: Generate contour plots for two-parameter sensitivity studies

5. **`EPA_CHP_System_Specs`**: A class that contains existing EPA CHP System Specifications from the [EPA Catalog of CHP Technologies](https://www.epa.gov/sites/production/files/2015-07/documents/catalog_of_chp_technologies.pdf).

### CPI Data Retrieval

`getAnnualCPI.py` - A module that retrieves annual Consumer Price Index (CPI) data from the Federal Reserve Economic Data (FRED) API. This is used to adjust economic calculations for inflation over time.

### Market Study Tools

`DGMarketStudy.py` - Contains the `MarketStudy` class for running comprehensive two-parameter sensitivity studies across multiple regions, years, and sectors. This class builds portfolios of distributed generation market assessments.

## Usage

### Basic EIA Data Query Example

```python
from EnergyMarketTools.EIADataQuery import EIAStateQuery

# Query data for Connecticut commercial sector
ct_data = EIAStateQuery(state='CT', sector='COM')
```

### Distributed Generation Value Proposition Example

```python
from EnergyMarketTools.DGValueProp import DGValProp, SensitivityStudy

# Run a sensitivity study for a specific region
study = SensitivityStudy(
    region='NY',
    year=2015,
    sector='C'  # Commercial
)
```

### CPI Data Retrieval Example

```python
from EnergyMarketTools.getAnnualCPI import getAnnualCPI

# Get annual CPI data
cpi_data = getAnnualCPI(displayData=True, plotData=True)
```

## Project Structure

```
EnergyMarketTools/
├── EnergyMarketTools/          # Main package directory
│   ├── DGValueProp.py         # Distributed generation value proposition classes
│   ├── DGMarketStudy.py       # Market study tools
│   ├── EIADataQuery.py        # EIA API query classes
│   ├── EIADataQuery_pd.py     # Pandas-based EIA queries
│   ├── getAnnualCPI.py        # FRED API CPI data retrieval
│   ├── parula_cmap.py         # Custom colormap utilities
│   └── RandomData.py          # Data generation utilities
├── setup.py                    # Package installation configuration
└── README.md                   # This file
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Author

**David Tew**
- Email: davetew@alum.mit.edu
- GitHub: [@davetew](https://github.com/davetew)

## Acknowledgments

This project uses data from:
- U.S. Department of Energy's Energy Information Administration (EIA)
- Federal Reserve Economic Data (FRED) from the Federal Reserve Bank of St. Louis
- EPA Combined Heat and Power (CHP) Partnership
