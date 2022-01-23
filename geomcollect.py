# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 13:06:00 2020

@author: fergal
"""

from ipdb import set_trace as idebug
import pandas as pd
import numpy as np


from frm.anygeom import AnyGeom
import frm.plots as fplots
import rtree

"""
You probably want to use MatchGeom in preference to this class
"""

class GeomCollection():
    """Quick and dirty code to figure out which of a set of geometries
    contains the requested geometry.

    Ensures a requested geom is considered contained even if they
    share an edge.

    Assumes none of the input geometries overlap (e.g they are
    precincts)
    """
    def __init__(self, geom_df):
        self.size = len(geom_df)
        self.geom_df = geom_df
        self.geom_tree = self.create_tree()

    def create_tree(self):
        tree = rtree.index.Index(interleaved=False)
        for i, row in self.geom_df.iterrows():
            geom  = row.geom
            env = geom.GetEnvelope()
            tree.insert(i, env)
        return tree

    def measure_overlap(self, shape):
        geom = AnyGeom(shape).as_geometry()
        env = geom.GetEnvelope()
        wh = list(self.geom_tree.intersection(env))

        frac_overlap = np.zeros(self.size, dtype=float)
        for i in wh:
            gi = self.geom_df.geom.iloc[i]
            intersection = geom.Intersection(gi)
            frac_overlap[i] = intersection.Area() / gi.Area()
        
        df = pd.DataFrame()
        df['frac'] = frac_overlap 
        df['name'] = self.geom_df.name
        return df

    def plot(self, *args, **kwargs):
        for geom in self.geom_df.geom:
            fplots.plot_shape(geom, *args, **kwargs)
