from ipdb import set_trace as idebug
import numpy as np
import rtree 

"""
This is untested
"""

#Functions for determining if a small geometry is associated with
#a large geometry
def contains(big_geom, small_geom):
    return big_geom.Contains(small_geom)


def overlaps(big_geom, small_geom, min_frac=.5):
    """Returns true if > 50% of small_geom is inside big_geom"""
    inter = big_geom.Intersection(small_geom)
    frac = inter.Area() / small_geom.Area()
    return frac >= min_frac


def intersects(big_geom, small_geom):
    return big_geom.Intersects(small_geom)


    

class GeomMatcher():
    """Effeciently match sets of geometries to each other.
    
    The mental model is that we have a set of many small geometries
    which we want to associate with a short list of large geometries
    
    Each small geometry is associated with zero or one large 
    geometries. If you want to know the fractional overlap you need
    to go back and compute that separately.
    
    The class builds an rtree index to do the work faster
    """
    
    def __init__(self, small_geoms):
        """
        Inputs
        -------
        small_geoms
            (list) A long list of small geometries
        """
        self.small = small_geoms
        self.index = self.create_index(self.small)
                  
            
    def match(self, big, is_member_func=contains):
        """Assign each of the many small geoms to a geometry in big 
        
        Inputs
        ---------
        big 
            (list) A (short) list of large geometries)
        is_member_func
            (func) A function that determines if the small geometry
            should be associated with a specific large geometry.
            
        Returns
        --------
        An array of len(small_geoms) of ints  with the number indicating 
        the index into big of the geometry the small geometry is associated
        with.
        
        Returns an array of ints. return[i] == 4 => small[i] is inside big[4]
        """
        
        out = -1 * np.ones(len(self.small))
        for i in range(len(big)):
            geom = big[i]
            wh = self.find_matching_geoms(geom, is_member_func)
            out[wh] = i 
        return out 

    def create_index(self, geoms):
        index = rtree.index.Index()

        for i, g in enumerate(geoms):
            if g.IsEmpty():
                continue 
            env = g.GetEnvelope()
            index.insert(i, env)
        return index    

    def find_matching_geoms(self, big_geom, is_member_func):
        env = big_geom.GetEnvelope()

        #elements of indices overlap in their envelopes
        indices = self.index.intersection(env)
        indices = list(indices)
        
        #Filter to just those elements that actual have membership of big_geom
        f = lambda x: is_member_func(big_geom, self.small[x])
        wh = list(filter(f, indices))
        
        #Get their location in the original array
        #wh = list(map(lambda x: x.object[0], indices))
        return wh
            
      
