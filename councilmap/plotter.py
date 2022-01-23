from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from frm.anygeom import AnyGeom
from frm.parmap import parmap
import frm.mapoverlay as fmo
import frm.get_geom as fgeom
import frm.plots as fplots


class PlotController():
    def __init__(self, **kwargs):
        self.inventory = dict()
        self.inventory.update(kwargs)
    
    def add(self, name, plotter):
        self.inventory[name] = plotter
        
    def render(self):
        axl = plt.axis()
        plt.clf()
        
        for k in self.inventory:
            self.inventory[k].render()

        if axl[2] > 0:  
            plt.axis(axl)
            

class Plotter():
    def __init__(self, is_visible=True):
        self.is_visible = is_visible
    
    def set_visible(self, is_visible):
        self.is_visible = is_visible
        
    def toggle(self,):
        self.is_visible = not self.is_visible 
    
    def render():
        raise NotImplementedError()
    
    
class MapOverlay(Plotter):
    def render(self):
        #plt.pause(.01) #Force axes to update
        if self.is_visible:
            fmo.drawMap()
        
      
class PolygonPlotter(Plotter):
    def __init__(self, names, geoms, **kwargs):
        self.names = names 
        self.geoms = geoms
        assert( len(self.names) == len(self.geoms) )
               
        self.label = kwargs.pop('label', False)
        
        self.kwargs = kwargs
        is_visible = kwargs.pop('is_visible', True)
        Plotter.__init__(self, is_visible)
        
    def render(self):
        if not self.is_visible:
            return 
        
        for n, g in zip(self.names, self.geoms):
            fplots.plot_shape(g, **self.kwargs)

            if self.label:
                centroid = g.Centroid()
                plt.text(
                    centroid.GetX(), 
                    centroid.GetY(), 
                    n, 
                    fontdict=self.kwargs['fontdict']
                )
                

class FillPlotter(Plotter):
    def __init__(self, names, geoms, **kwargs):
        self.names = names 
        self.geoms = geoms
        self.cmap = kwargs.pop('cmap', plt.cm.Set1 )
                               
        assert( len(self.names) == len(self.geoms) )
               
        self.kwargs = kwargs
        is_visible = kwargs.pop('is_visible', True)
        Plotter.__init__(self, is_visible)
        
    def render(self):
        if not self.is_visible:
            return 

        index  = np.arange(len(self.geoms))
        fplots.chloropleth(self.geoms, index, cmap=self.cmap)
    
    
class CsvFilePolyPlotter(PolygonPlotter):
    def __init__(self, fn, name='name', geom='geom', **kwargs):
        self.fn = fn
        self.nameCol = name 
        self.geomCol = geom 
        self.watch = kwargs.pop('watch', False)

        PolygonPlotter.__init__(self, [], [], **kwargs)
        self.load(fn)
        self.fresh = True 
        
    def load(self, fn):
        df = pd.read_csv(fn, index_col=0)
        self.names = df[self.nameCol]
        self.geoms = df[self.geomCol]
        
        
    def render(self):
        if self.watch and is_file_changed(self.fn):
            self.load(self.fn)
        PolygonPlotter.render(self)
            


class CsvFillPlotter(FillPlotter):
    def __init__(self, fn, name='name', geom='geom', **kwargs):
        self.fn = fn
        self.nameCol = name 
        self.geomCol = geom 
        self.watch = kwargs.pop('watch', False)

        FillPlotter.__init__(self, [], [], **kwargs)
        self.load(fn)
        
    def load(self, fn):
        df = pd.read_csv(fn, index_col=0)
        self.names = df[self.nameCol]
        self.geoms = df[self.geomCol]
        
        
    def render(self):
        if self.watch and is_file_changed(self.fn):
            self.load(self.fn)
        FillPlotter.render(self)
            
import os 
def is_file_changed(fn):

    #create a static variable
    if not hasattr('is_file_changed', 'inventory'):
        is_file_changed.inventory = dict()
    
    last_modified = os.path.getmtime(fn)
    if fn not in is_file_changed.inventory:
        is_file_changed.inventory[fn] = last_modified
        return True 

    if last_modified > is_file_changed.inventory[fn]:
        is_file_changed.inventory[fn] = last_modified
        return True 
    
    return False
    
