from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import tully3.reporter as reporter
import tully3.plotter as plotter
import common 


def init(fn):
    state = dict()
    
    state['plot_controller'] = create_plotters(fn)
    state['report_controller'] = create_reporters(fn)
    return state 


def create_plotters(fn):
    
    pc = plotter.PlotController()
    
    tmp = OrigDistricts(None, color='r', lw=3)
    pc.add('orig_districts', tmp)

    tmp = CommissionDistricts(None, color='m', lw=3, ls=":")
    tmp.set_visible(False)
    pc.add('comm_districts', tmp)

    tmp = PrecinctLines(None, cmap=plt.cm.RdBu)
    tmp.set_visible(False)
    pc.add('precincts', tmp)

    tmp = CensusPlace(None, color='b', lw=1)
    pc.add('places', tmp)

    cmap = plt.cm.bone_r
    cmap.set_under('#FF000000')
    tmp = BlackPopLayer(None, cmap=cmap)
    pc.add('black_pop', tmp)

    tmp = plotter.MapOverlay()
    pc.add('osm', tmp)

    return pc 


def create_reporters(fn):
    rep = reporter.ReportController()
    
    tmp = reporter.DemographicsReporter()
    rep.add('demographic', tmp)
    
    precinct_df = common.load_vote_data_by_precinct()
    tmp = reporter.PartisanReporter(precinct_df)
    rep.add('partisan', tmp)
    return rep
    
class OrigDistricts(plotter.CsvFilePolyPlotter):
    def load(self, fn):
        df = common.load_district_lines('v2010')
        self.names = df['name']
        self.geoms = df['geom']

class CommissionDistricts(plotter.CsvFilePolyPlotter):
    def load(self, fn):
        df = common.load_district_lines('commission')
        self.names = df['name']
        self.geoms = df['geom']
    
class PrecinctLines(plotter.CsvFillPlotter):
    def load(self, fn):
        df = common.load_vote_data_by_precinct()
        self.names = df['name']
        self.geoms = df['geom']

class CensusPlace(plotter.CsvFilePolyPlotter):
    def load(self, fn):
        df = common.load_census_places()
        self.names = df['name']
        self.geoms = df['geom']


import frm.plots as fplots
class BlackPopLayer(plotter.CsvFillPlotter):
    def load(self, fn):
        df = common.load_census_tracts(fn)
        self.names = df['name']
        self.geoms = df['geom']
        self.BlackPop = df['TotalBlack']
        
    def render(self):
        if not self.is_visible:
            return 

        vals = self.BlackPop
        fplots.chloropleth(self.geoms, vals, cmap=self.cmap, vmin=500)
    
