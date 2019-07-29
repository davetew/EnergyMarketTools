#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  1 18:23:45 2017

@author: David.Tew
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from EnergyMarketTools.DGValueProp import SensitivityStudy
from EnergyMarketTools.EIADataQuery import EIAStateQuery
from EnergyMarketTools.parula_cmap import parula_cmap

class MarketStudy:    
    """Run a two parameter sensitivity study in the specified regions, over 
    the specified years, and for the specified sectors. A study portfolio is 
    returned in the form of a triply nested dictionary."""    
    def __init__(self,Regions=['US'],Years=[2015],Sectors=['COM'],
                     x_param_name=None,
                     x_param_values=None,
                     y_param_name=None,
                     y_param_values=None,
                     electric_efficiency = 0.7,
                     thermal_efficiency = '(1-electric_efficiency)/2',
                     installed_price_dol_W = 3,
                     maint_cost_dol_kWh = 0.02,
                     life_yrs = 20,
                     elec_capacity_utilization = 0.80,
                     therm_capacity_utilization = 0.25,
                     baseline_thermal_efficiency = 0.9,
                     inflation_rate = 0.02,
                     discount_rate = 0.15,
                     grid_baseline_elec_efficiency=0.34):
        
        self.Sectors = Sectors
        self.Years = Years
        self.Regions = Regions
        self.grid_baseline_elec_efficiency = grid_baseline_elec_efficiency
        
        # Array of zeros for initialization purposes
        SensZeros = np.zeros((len(y_param_values),len(x_param_values)))
        
        # Empty dictionary for market study results
        self.studyPortfolio = {sector: {year: {region: None for region in Regions} 
            for year in Years} for sector in Sectors}
        
        self.TotalMarket_TWh = {sector: {year: 0 for year in Years} for sector in Sectors}
        self.AddressedMarket_TWh = {sector: {year: SensZeros for year in Years} for sector in Sectors}
        self.TotalMarketPen = {sector: {year: SensZeros for year in Years} for sector in Sectors}
        self.PrimaryEnergySavings_TWh = {sector: {year: SensZeros for year in Years} for sector in Sectors}            
        self.PrimaryEnergySavings_Quads = {sector: {year: SensZeros for year in Years} for sector in Sectors} 
        
        for sector in Sectors:
            for year in Years:
                for region in Regions:
                    
                    self.studyPortfolio[sector][year][region] = \
                             SensitivityStudy(Region=region, Year=year, Sector=sector, 
                             x_param_name=x_param_name,
                             x_param_values=x_param_values,
                             y_param_name=y_param_name,
                             y_param_values=y_param_values,
                             electric_efficiency = electric_efficiency,
                             thermal_efficiency = thermal_efficiency,
                             installed_price_dol_W = installed_price_dol_W,
                             maint_cost_dol_kWh = maint_cost_dol_kWh,
                             life_yrs = life_yrs,
                             elec_capacity_utilization = elec_capacity_utilization,
                             therm_capacity_utilization = therm_capacity_utilization,
                             baseline_thermal_efficiency = baseline_thermal_efficiency,
                             inflation_rate = inflation_rate,
                             discount_rate = discount_rate)
                    
                    region_TotalMarket_TWh = self.studyPortfolio[sector][year][region].NetGeneration_TWh
                    region_AddressedMarket_TWh = region_TotalMarket_TWh * \
                           self.studyPortfolio[sector][year][region].get_val_metric('MaxMarketPen')          
                                      
                    if self.TotalMarket_TWh[sector][year] == 0:
                        self.TotalMarket_TWh[sector][year] = region_TotalMarket_TWh
                        self.AddressedMarket_TWh[sector][year] = region_AddressedMarket_TWh        
                    else:
                        self.TotalMarket_TWh[sector][year] += region_TotalMarket_TWh
                        self.AddressedMarket_TWh[sector][year] += region_AddressedMarket_TWh 
                                            
                    #print('Total Market (TWh) = %s' % self.TotalMarket_TWh)
    
                self.TotalMarketPen[sector][year] = self.AddressedMarket_TWh[sector][year] / \
                                    self.TotalMarket_TWh[sector][year]
                                    
                self.PrimaryEnergySavings_TWh[sector][year] = \
                                     self.AddressedMarket_TWh[sector][year]/self.grid_baseline_elec_efficiency * ( 1 - 
                                     self.grid_baseline_elec_efficiency / 
                                     self.studyPortfolio[sector][year][region].get_val_metric('Effective_Electric_Efficiency') )                            
                                    
                self.PrimaryEnergySavings_Quads[sector][year] = self.PrimaryEnergySavings_TWh[sector][year] / 293.1  
                                
        
    def contour_plot(self,sector,year,region=None,metric=None):
        """Market penetration contour plot."""
        
        if metric in dir(self.studyPortfolio[sector][year][region].study[0][0].out):
            
            """Draw a contour plot for the specified metric in the specified
            sector, year and region."""
            fig, ax = self.studyPortfolio[sector][year][region].contour_plot(metric)
            
        else:
            """Draw total market penetration contours."""
            z_param = getattr(self,metric)[sector][year]
            
            figtitle = metric + ' ' + sector + ' ' + str(year)
            fig = plt.figure(num=figtitle)
        
            ax = plt.subplot(1,1,1)
    
            cmap = cm.jet #cm.PRGn
            
            if metric is 'TotalMarketPen':
                levels = np.linspace(0,1,21)
            else:
                levels = np.linspace(np.amin(z_param),np.amax(z_param),21)
                        
            norm = cm.colors.Normalize(vmax=levels.max(), vmin=levels.min())
    
            plt.contourf(self.studyPortfolio[sector][year][region].x_param_values,
                         self.studyPortfolio[sector][year][region].y_param_values,
                         z_param,levels, cmap=cm.get_cmap(cmap, len(levels)-1),norm=norm)

            plt.colorbar(format='%.1f'); plt.autoscale(False)
     
            plt.xlabel(self.studyPortfolio[sector][year][region].pretty_label(
                    self.studyPortfolio[sector][year][region].x_param_name))
            plt.ylabel(self.studyPortfolio[sector][year][region].pretty_label(
                    self.studyPortfolio[sector][year][region].y_param_name))
            #plt.title(figtitle)
            
            plt.contour(self.studyPortfolio[sector][year][region].x_param_values,
                        self.studyPortfolio[sector][year][region].y_param_values,
                        z_param,levels,linewidths=0.25,colors='k')
            
            # Draw 1 Quad/year contour
            z_Quad = getattr(self,'PrimaryEnergySavings_Quads')[sector][year]
            plt.contour(self.studyPortfolio[sector][year][region].x_param_values,
                        self.studyPortfolio[sector][year][region].y_param_values,
                        z_Quad,levels=[1],linewidths=1,linestyles='dashed',colors='w')
            
            # Draw 50% market penetration contour
            z_Quad = getattr(self,'TotalMarketPen')[sector][year]
            plt.contour(self.studyPortfolio[sector][year][region].x_param_values,
                        self.studyPortfolio[sector][year][region].y_param_values,
                        z_Quad,levels=[0.5],linewidths=1,linestyles='dotted',colors='r')
            
            
            plt.tight_layout()
 
        return fig, ax
        
            
            
    

