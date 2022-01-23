import pandas as pd
import numpy as np

import frm.support 
import common
import json


class BlockListToShapes():
    """Convert a dataframe mapping census blocks 
    to districts into a set of geometries
    """
    
    def __init__(self):
        self.cache = dict()
        
    def __call(self, df):
        return self.get_district_boundaries(df)
    
    def get_district_boundaries(self, df):
        districts = df.districts.values 
        hash_value = hash(tuple(districts))
        
        if hash_value in self.cache:
            return self.cache[hash_value]
    
        #Clear cache
        self.cache = dict()
        df = self._compute_district_boundaries(df)
        self.cache[hash_value] = df 
        return df 
    
    def _compute_district_boundaries(self, df):
        district_names = list(set(df.districts))
        
        geoms = []
        union = frm.support.union_collection
        for dd in district_names:
            idx = df.district == dd
            df2  = df[idx] 
    
            geoms.append(union(df2.geom.values ))

        out = pd.DataFrame()
        out['district'] = district_names
        out['geom'] = geoms
        return out


class ReportController():
    def __init__(self):
        self.inventory = dict()
        
    def add(self, name, obj):
        self.inventory[name] = obj 

    def text(self, cb):
        out = []
        for name in self.inventory:
            out.append(name)
            out.extend(self.inventory[name].text(cb))
            
        return out

class Reporter():
    """
    Input
    For demographics:
    Input: CB --> district mapping
    Return: dict of counts 
    
    For precincts
    Input: District geometries
    Return dict of counts
    
    Maybe I can pass in a mapping and call
    a helper class that computes the 
    district boundaries, caching results as necessary
    
    """
    
    #Shared between all objects of this class?
    districtGeomCreator = BlockListToShapes()
    def __init__(self):
        pass 
    
    def calculate(self):
        raise NotImplementedError
    
    
    def text(self, cb):
        raise NotImplementedError
    
    
    def json(self):
        return json.dumps(self.calculate())
    
    def html(self):
        raise NotImplementedError
    
    
    
class DemographicsReporter(Reporter):
    """Calculate Population and Demographics of districts defined by census blocks"""
    def calculate(self, cb):
        gr = cb.groupby('district')
        out = dict()
        out['TotalPop'] = gr.TotalPop.sum()
        out['TotalBlack'] = gr.TotalBlack.sum()
        return out
    
    def text(self, cb):
        data = self.calculate(cb)
        
        out = []
        out.append("Total Population: %6i" %(data['TotalPop']))
        out.append("Total Black Population: %6i" %(data['TotalBlack']))
        out.append("Percent Black: %6i" %(100 * data['TotalBlack']/ float(data['TotalPop'])))                
        
        return out
    
    
class PartisanReporter(Reporter):
    """Calculate partisan lean of districts defined by census blocks"""
    def __init__(self, precinct_df):
        self.precinct_df = precinct_df
        self.races = "Clinton2016 Jealous2018 JohnnyO2018 Biden2020".split()
        
    def calculate(self, cb):
        district_df = Reporter.districtGeomCreator(cb)
        
        overlap = common.compute_frac_overlaps(district_df.geom, self.precinct_df)    

        #Put this in a dataframe, with candidates for columns
        out = pd.DataFrame(index=district_df.name, columns=self.races)
        
        for i, d in enumerate(out.index):
            for r in out.columns:
                count = np.sum(overlap[i] * self.precinct_df[r])
                out.iloc[i, r] = count
        return out
    
    def text(self, cb):
        df = self.calculate(cb)

        #Placeholder
        return [df.to_csv()]
    
