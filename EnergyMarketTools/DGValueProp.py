#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 14:51:27 2017

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
    
@author: David.Tew
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from EIADataQuery import EIAStateQuery
from parula_cmap import parula_cmap, parula_cmap_r

#%% Define class structures for storing DG value proposition data
class DGOut:
    """Distributed generation value proposition metrics and a 
    market penetration estimate."""
    def __init__(self,NPV_dol_kWh=float("NaN"), IRR=float("NaN"), 
                 PB_yrs=float("NaN"), LCOE_dol_kWh = float("NaN"), 
                 MaxMarketPen = float("NaN"), Effective_Electric_Efficiency = float("NaN") ):
        self.NPV_dol_kWh = NPV_dol_kWh
        self.IRR = IRR
        self.PB_yrs = PB_yrs
        self.LCOE_dol_kWh = LCOE_dol_kWh
        self.MaxMarketPen = MaxMarketPen
        self.Effective_Electric_Efficiency = Effective_Electric_Efficiency
        
class DGIn:
    """Input parameters for distributed generation value proposition assessment."""
    def __init__(self, electric_efficiency = 0.7,
                 thermal_efficiency = 0,
                 installed_price_dol_W = 3,
                 maint_cost_dol_kWh = 0.02,
                 life_yrs = 20,
                 elec_capacity_utilization = 0.85,
                 therm_capacity_utilization = 0.25,
                 baseline_thermal_efficiency = 0.9,
                 inflation_rate = 0.02,
                 discount_rate = 0.15,
                 elec_rate_dol_kWh = float("NaN"),
                 ng_rate_dol_kWh = float("NaN")):
        self.electric_efficiency = electric_efficiency
        if isinstance(thermal_efficiency,str):
            self.thermal_efficiency = eval(thermal_efficiency)
        else:
            self.thermal_efficiency = thermal_efficiency
        self.installed_price_dol_W = installed_price_dol_W
        self.maint_cost_dol_kWh = maint_cost_dol_kWh
        self.life_yrs = life_yrs
        self.elec_capacity_utilization = elec_capacity_utilization
        self.therm_capacity_utilization = therm_capacity_utilization
        self.baseline_thermal_efficiency = baseline_thermal_efficiency
        self.inflation_rate = inflation_rate
        self.discount_rate = discount_rate
        self.elec_rate_dol_kWh = elec_rate_dol_kWh
        self.ng_rate_dol_kWh = ng_rate_dol_kWh
            
    def set_spread(self,StateDataSet):
        """Set the spark spread using rate data from an object of type
        EIAStateDataSet()"""
        self.elec_rate_dol_kWh = StateDataSet.elec_rate_dol_kWh
        self.ng_rate_dol_kWh = StateDataSet.ng_rate_dol_kWh

 
class DGValProp:
    """
    DGValProp is a class that contains the the input assumptions and output economic
    value proposition estimate for a specific distributed generation scenario.  It
    consists of two sub-classes:  DGin() and DGOut().  DGin() contains the input 
    assumptions and DGOut() contains the output value proposition metrics.        
    
    """    
    def __init__(self,inp=DGIn()):
        self.inp = inp
                                        
    @property
    def out(self):
        
        def Maximum_Market_Penetration(PB_yrs):   
            """ Maximum market penetration model.  MMP = fn(PB_years)"""           
            # Model constants
            A, sigma = 0.3193, 0.1274
            # Estimated maximum market penetration
            MMP = np.where(PB_yrs >= 0, 
                           A/np.sqrt(2*np.pi)/sigma * np.exp(-(PB_yrs/self.inp.life_yrs/sigma)**2/2), 0)
            #MMP = np.where(np.isnan(MMP), 0, MMP)
            return MMP
        
        def DF():
            """Calculate the discount factor (DF). The discount factor is 
            implicitly defined as follows for constant operating cashflows (C_i)
            after an initial investment (C_0).
            
            NPV = -C_0 + sum(C_i/(1+r)^i) = -C_0 + C_i*sum(1/(1+r)^i)
                  -C_0 + C_i * DF
            
            DF = sum(1/(1+r)^i)
            """
            return np.sum(1/(1+self.inp.discount_rate)**np.array(range(1,self.inp.life_yrs+1)))
            
        def LCOE():
            """Calculate the levelized cost of electricity in $/kWh"""
            return self.inp.installed_price_dol_W*1000/8760/ \
                         self.inp.elec_capacity_utilization/DF() + \
                         self.inp.ng_rate_dol_kWh/self.inp.electric_efficiency + \
                         self.inp.maint_cost_dol_kWh - self.inp.ng_rate_dol_kWh * \
                         self.inp.thermal_efficiency / self.inp.electric_efficiency / \
                         self.inp.baseline_thermal_efficiency * \
                         self.inp.therm_capacity_utilization 
                         
        def Effective_Electric_Efficiency():
            """Calculate the effective electric efficiency."""
            return self.inp.electric_efficiency / (1 - self.inp.thermal_efficiency / 
                                               self.inp.baseline_thermal_efficiency * 
                                               self.inp.therm_capacity_utilization / 
                                               self.inp.elec_capacity_utilization)

                                
        # Calculate annual cashflows in $/kWh
        CashFlows_dol_kWh = np.zeros(self.inp.life_yrs+1)
        
        # Initial capital expenditures is assumed to occur in the first year
        CashFlows_dol_kWh[0] = -self.inp.installed_price_dol_W*1000/8760/ \
                         self.inp.elec_capacity_utilization
                         
        # Operating cash flows -- assumed to be in years 1 through life_yrs
        for i in range(1,self.inp.life_yrs+1):          
            CashFlows_dol_kWh[i] = ( self.inp.elec_rate_dol_kWh - 
                         self.inp.ng_rate_dol_kWh/self.inp.electric_efficiency - 
                         self.inp.maint_cost_dol_kWh + self.inp.ng_rate_dol_kWh * 
                         self.inp.thermal_efficiency / self.inp.electric_efficiency /
                         self.inp.baseline_thermal_efficiency *
                         self.inp.therm_capacity_utilization) * (1+self.inp.inflation_rate)**i
        
        # print('Cash Flows ($/kWh) = %s' % CashFlows_dol_kWh)
        
        # Try to calculate IRR
        try:
            irr = np.irr(CashFlows_dol_kWh)
        except ValueError:  # IRR calc did not converge
            irr = float("NaN")
        
        # Simple payback period
        PB_yrs = -CashFlows_dol_kWh[0] / CashFlows_dol_kWh[1]
        
        return DGOut(NPV_dol_kWh=np.npv(self.inp.discount_rate,CashFlows_dol_kWh),
                    IRR = irr,
                    PB_yrs = PB_yrs,
                    LCOE_dol_kWh = LCOE(),
                    MaxMarketPen = Maximum_Market_Penetration(PB_yrs),
                    Effective_Electric_Efficiency = Effective_Electric_Efficiency()) 

class SensitivityStudy:
    """
    Run two-parameter DG value proposition sensitivity study for a specific 
    region (e.g. state, US), year, and sector (e.g. COM).  In a study, DG system
    input characteristics are varied over the specified range while holding the
    remainder at constant/nominal values.
    
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

    """
    def __init__(self, Region='US', Year=2015, Sector='COM', 
                 y_param_name=None,
                 y_param_values=None,
                 x_param_name=None,
                 x_param_values=None,
                 electric_efficiency = 0.7,
                 thermal_efficiency = 0,
                 installed_price_dol_W = 1.8,
                 maint_cost_dol_kWh = 0.02,
                 life_yrs = 20,
                 elec_capacity_utilization = 0.85,
                 therm_capacity_utilization = 0.25,
                 baseline_thermal_efficiency = 0.9,
                 inflation_rate = 0.02,
                 discount_rate = 0.15):
        
        self.Region = Region
        self.Year = Year
        self.Sector = Sector
        
        self.RegionalData = EIAStateQuery(Region,Sector)
        self.NetGeneration_TWh = self.RegionalData.Data[Year].net_generation_kWh/1e9
                                                     
        self.x_param_name = x_param_name
        self.x_param_values = x_param_values
        self.y_param_name = y_param_name
        self.y_param_values = y_param_values
        
        # Execute sensitivity study & calcuate economic benefit metrics for each combination of x_param_values & y_param_values
        Study = [[ None for i in range(len(x_param_values))] for j in range(len(y_param_values))]
        for i, x_param in enumerate(x_param_values):
            for j, y_param in enumerate(y_param_values):
                
                # Create an instance of the input class for the nominal scenario    
                inp = DGIn(electric_efficiency=electric_efficiency,
                           thermal_efficiency=thermal_efficiency,
                           installed_price_dol_W=installed_price_dol_W,
                           maint_cost_dol_kWh=maint_cost_dol_kWh,
                           life_yrs=life_yrs,
                           elec_capacity_utilization=elec_capacity_utilization,
                           therm_capacity_utilization=therm_capacity_utilization,
                           baseline_thermal_efficiency=baseline_thermal_efficiency,
                           inflation_rate=inflation_rate,
                           discount_rate=discount_rate)
                
                # Update the energy rates for the specified state & year
                inp.set_spread(self.RegionalData.Data[Year])
                
                # Update the instance with the new x_param & y_param
                setattr(inp,x_param_name,x_param)
                setattr(inp,y_param_name,y_param)
                
                Study[j][i] = DGValProp(inp)
        self.study = Study
    
    # Scatter plot method    
    def x_plot(self,val_metric='NPV_dol_kWh'):
         
         plt.figure(num='XY Scatter:  ' + val_metric + ':  ' + 
                    self.RegionalData.Region + ' ' + str(self.Year)) 
         for j, y_param in enumerate(self.y_param_values):
             plt.plot(self.x_param_values,[getattr(self.study[j][i].out,val_metric)
                 for i in range(len(self.x_param_values))],
                 label=self.y_param_name + ' = ' + str(y_param) )
         plt.xlabel(self.x_param_name)
         plt.ylabel(val_metric)
         plt.title( self.RegionalData.Region + ' ' + str(self.Year) )
         plt.grid; plt.legend()
         
    def get_val_metric(self,val_metric):
        return np.array([[getattr(self.study[j][i].out,val_metric) 
                    for i in range(len(self.x_param_values))]
                    for j in range(len(self.y_param_values))])
                 
    def contour_plot(self,val_metric='NPV_dol_kWh'):

        z_param = self.get_val_metric(val_metric)
                
        fig = plt.figure(num='Contour:  ' + val_metric + ':  ' + 
                    self.RegionalData.Region + ' ' + str(self.Year))
        
        ax = plt.subplot(1,1,1)
        
        if val_metric is 'PB_yrs':
            # Inverted colormap for the big is bad metrics
            cmap = parula_cmap_r()
            l_max = np.ceil(np.amin([np.amax(z_param),self.study[0][0].inp.life_yrs]))
            cbar_format = '%d'
            levels = np.linspace(0,l_max,l_max+1)
        elif val_metric is 'LCOE_dol_kWh':
             # Inverted colormap for the big is bad metrics
            cmap = parula_cmap_r()
            levels = np.linspace(np.amin(z_param),np.amax(z_param),21)
            cbar_format = '%.2f'
        elif val_metric is 'MaxMarketPen' or val_metric is 'Effective_Electric_Efficiency':
            # Normal colormap for the big is good metrics
            cmap = cm.jet  
            levels = np.linspace(0,1,21)
            cbar_format = '%.2f'
        else:
            # Normal colormap for the big is good metrics
            cmap = parula_cmap()
            levels = np.linspace(np.amin(z_param),np.amax(z_param),21)
            cbar_format = '%.2f'
            
        norm = cm.colors.Normalize(vmax=levels.max(), vmin=levels.min())
        
            
        plt.contourf(self.x_param_values,self.y_param_values,z_param,levels,
                     cmap=cm.get_cmap(cmap, len(levels)-1),norm=norm)
        plt.colorbar(format=cbar_format); #plt.autoscale(False)
        plt.xlabel(self.pretty_label(self.x_param_name))
        plt.ylabel(self.pretty_label(self.y_param_name))
        plt.contour(self.x_param_values,self.y_param_values,z_param,levels,
                    linewidths=0.25,colors='k')
        #plt.title(self.pretty_label(val_metric) + ':  ' + self.RegionalData.Region + ' ' + str(self.Year) )
        plt.tight_layout()
        
        return fig, ax
    
    def pretty_label(self,param_name):
        """Return a "nicely-formatted" axis label or title given the specified 
        parameter name.  If no "nicely-formated" version is available, the 
        parameter name is simply returned."""
        return {'electric_efficiency': '$\eta_{electric}$',
                'installed_price_dol_W': 'Installed Cost ($/W)',
                'PB_yrs': 'Payback Period (years)',
                'NPV_dol_kWh': 'NPV ($/kWh)',
                'LCOE_dol_kWh': 'LCOE ($/kWh)'}.get(param_name,param_name)
                  
"""EPA CHP System Specifications from -- 
https://www.epa.gov/sites/production/files/2015-07/documents/catalog_of_chp_technologies.pdf
The electric efficiencies specied below are on an LHV basis."""
class EPA_CHP_System_Specs:
    
    def __init__(self):
    
        self.specs =  {'SI Engine': {
                    'Power_kW': np.array([100, 633, 1121, 3326, 9341]),
                    'electric_efficiency': np.array([0.30, 0.38, 0.41, 0.45, 0.46]),
                    'installed_price_dol_W': np.array([2900, 2837, 2366, 1801, 1433])/1000, 
                    'Maint_Cost_dol_kWh': np.array([0.024, 0.021, 0.019, 0.016, 0.009])},
                'Gas Turbine': {
                    'Power_kW': np.array([3304, 7038, 9950, 20336, 44488]),
                    'electric_efficiency': np.array([0.27, 0.32, 0.30, 0.37, 0.40]),
                    'installed_price_dol_W': np.array([3281, 2080, 1976, 1518, 1248])/1000, 
                    'Maint_Cost_dol_kWh': np.array([0.013, 0.012, 0.012, 0.009, 0.009])},
                'Microturbine': {
                    'Power_kW': np.array([28, 61	, 90, 240, 320, 950]),
                    'electric_efficiency': np.array([0.24, 0.26, 0.30, 0.29, 0.31, 0.30]),
                    'installed_price_dol_W': np.array([4300, 3220, 3150, 2720, 2580, 2500])/1000,
                    'Maint_Cost_dol_kWh': np.array([0.013, 0.013, 0.016, 0.011, 0.009, 0.012]) },
                'Fuel Cell': {
                    'Power_kW': np.array([1, 2, 300, 400, 1400]),
                    'electric_efficiency': np.array([0.39,0.60, 0.52, 0.38,	 0.47]),
                    'installed_price_dol_W': np.array([22000, 23000, 10000, 7000, 4600])/1000, 
                    'Maint_Cost_dol_kWh': np.array([0.060, 0.055, 0.045, 0.036, 0.040])}}
        
        self.technologies = list(self.specs.keys())
        self.parameters = list(self.specs['SI Engine'].keys())
        
    def get_param(self,technology,parameter):
        
        return self.specs[technology][parameter]
    
    def scatter_plot_all_tech(self,x_param_name,y_param_name,legend_loc=0):
                
        for tech, data in self.specs.items():           
            plt.scatter(self.specs[tech][x_param_name], 
                        self.specs[tech][y_param_name],
                        label = tech, edgecolors = 'w', zorder = 1)
            plt.legend(loc=legend_loc)
                
