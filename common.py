from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from frmgis.anygeom import AnyGeom
import frmgis.get_geom as fgeom
import frmbase.dfpipeline as dfp
import frmplots.plots as fplots
import frmbase.support 

#import osgeo.gdal as gdal 
import osgeo.ogr as ogr 
import rtree
import os 

#gdal.UseExceptions()
ogr.UseExceptions()

npmap = frmbase.support.npmap

HOME = os.path.join(os.path.split(__file__)[0])

def load_district_lines(owner, fn=None):
    """
    
    Returns 
    -------
    A dataframe with columns (name geom)
    """
    func = dict()
    func['v2010'] = load_2010_district_lines
    func['aclu'] = load_aclu_district_lines
    func['commission'] = load_commission_district_lines

    if owner in func:
        df =  func[owner](fn)
    else:
        raise ValueError("Available maps are %s" %(list(func.keys())))

    assert frmbase.support.check_columns_in_df(df, "name geom".split())
    assert set(df.name) == set(np.arange(1, 8))
    assert isinstance(df.geom.iloc[0], ogr.Geometry)
    return df



def load_2010_district_lines(fn):
    if fn is None:
        fn = "/home/fergal/data/elections/shapefiles/councildistricts/districts.shp"

    df = fgeom.load_geoms_as_df(fn)
    mapper = dict(
        geoms='geom',
        COUNCILMAN='name',
    )
    df = df.rename(mapper, axis=1)
    df['name'] = df.name.astype(int)
    df = df.drop(['SHAPE_AREA', 'SHAPE_LEN'], axis=1)
    return df.sort_values('name')


def load_commission_district_lines(fn):
    if fn is None:
        fn = os.path.join(HOME, 'data/commission/proposed_districts.csv')
    
    districts = pd.read_csv(fn, index_col=0)
    
                       
    districts['name'] = districts.district
    districts['geom'] = list(map(lambda x: AnyGeom(x).as_geometry(), districts.geom))
    return districts


def load_aclu_district_lines(fn):

    if fn is None:
        fn =os.path.join(HOME, "data/aclu/Baltimore_County_8_28_draft.zip")
        
    districts = fgeom.get_geometries(fn)
    geoms = list(map(lambda x: x[0], districts))
    
    districts = pd.DataFrame()
    districts['geom'] = geoms
    districts['name'] = np.arange(1,8)
    return districts


def load_voter_rolls(year, path=None):
    if path is None:
        path = '/home/fergal/data/elections/voterrolls'
        
    years = {
        2017:'voterroll2017-11-27/voterroll2017.csv',
        2018:'voterroll2018-08-21/voterroll2018.csv',
        2021:'voterroll2021-07-07/voterroll2021.csv',
    }
    
    if year not in years:
        raise ValueError("Available years are %s" %(list(years.keys())))

    path = os.path.join(path, years[year])  
    df = pd.read_csv(path, index_col=0)
    return df
                         
                            

def load_census_tracts(fn=None):
    if fn is None:
        fn = os.path.join(HOME, "data/census_tracts/census_pop_data_2020.csv")

    pipeline = [
        dfp.Load(fn),
        dfp.AssertColExists("fips", "TotalPop"),
        dfp.RenameCols(dict(geoms='geom')),
        dfp.SetColumn('name', 'fips'),
        dfp.ApplyFunc('geom', lambda x: AnyGeom(x.geom).as_geometry()) 
    ]
    df = dfp.runPipeline(pipeline)
    return df 


def load_census_blocks(fn=None):
    if fn is None:
        fn = os.path.join(HOME, "data/census_blocks/block_level_population.csv")

    pipeline = [
        dfp.Load(fn),
        dfp.AssertColExists("fips", "TotalPop"),
        dfp.RenameCols(dict(geoms='geom')),
        dfp.SetColumn('name', 'fips'),
        dfp.ApplyFunc('geom', lambda x: AnyGeom(x.geom).as_geometry()) 
    ]
    df = dfp.runPipeline(pipeline)
    return df 


def load_census_places(fn=None):
    if fn is None:
        fn = os.path.join(HOME, "data/census_places/tl_2020_24_place.shp")
        
    df = fgeom.load_geoms_as_df(fn)
    pipeline = [
        dfp.AssertColExists("NAME", "geoms"),
        dfp.RenameCols(dict(NAME='name', geoms='geom')),
        dfp.ApplyFunc('geom', lambda x: AnyGeom(x.geom).as_geometry()) ,
        dfp.SelectCols("name", "geom")
    ]
    df = dfp.runPipeline(pipeline, df)
    return df 


def loadElectionResultsByPrecinct(
    year, 
    county="Baltimore", 
    primary=False, 
    party='Democratic', 
    path=None
):
    """Doesn't include precinct geometries"""
    
    if path is None:
        path = "/home/fergal/data/elections/MdBoEl"
    
    if primary:
        fn = f"{county}_By_Precinct_{party}_{year}_Primary.csv"
    else:
        fn = f"{county}_By_Precinct_{year}_General.csv"
    
    path = os.path.join(path, county, fn)
    df = pd.read_csv(path, index_col=0)
    
    mapper = {
        'Election Night Votes':'Votes',
        'Election Night Votes Against':'VotesAgainst',
        'Candidate Name':'Candidate',
        'Office Name':'Office',
    }
    
    df = df.rename(mapper, axis=1)
    f = lambda x, y: "%02i-%03i" % (x,y)
    df['Precinct'] = npmap(f, df['Election District'], df['Election Precinct'])
    
    cols = [
       'Election District', 
       'Election Precinct',
       'Office District', 
       'Winner',
       'Write-In?', 
    ]
    df = df.drop(cols, axis=1, errors='ignore')
    return df


def load_DOIP_turnout_by_precinct(year, county="Baltimore County", fn=None):
    """Load the number of DOIP voters from each party 
    
    DOIP means "day-of, in-person".
    
    Returns a dataframe of the number of registered voters in each 
    precinct in the requested county that showed up to vote in-person 
    on election day. Similar numbers for early voters do not seem to
    be available from the BoEl
    """
    
    if fn is None:
        fn = f"/home/fergal//data/elections/MdBoEl/turnout/turnout_general_{year}.csv"
    
    df = pd.read_csv(fn)
    df = df[df['LBE'] == county ]
    if len(df) == 0:
        raise ValueError(f"No data found for county {county}")
    
    #Pivot to get election day numbers. I can't find
    #votes per candidate for the early voting data
    df['PRECINCT'] = df.PRECINCT.str[1:]
    df = df.pivot(index='PRECINCT', columns='PARTY', values='POLLS')

    df2 = pd.DataFrame()
    df2['Precinct'] = df.index
    df2['DEM'] = df.DEMOCRAT.values
    df2['REP'] = df.REPUBLICAN.values
    df2['IND'] = (df.GREEN + df.LIBERTARIAN + \
                 df['OTHER PARTIES']  + df.UNAFFILIATED).values
    return df2 


def load_vote_data_by_precinct(geom_file=None, data_file=None):
    """
    Load the vote excess data I use to compute the partisan lean of a district
    """
    if data_file is None:
        data_file = os.path.join(HOME, 'data/precinct_data/tully_input.csv')
        
    #How much county wide canddiates won (or lost) this precinct
    pipeline = [
        dfp.Load(data_file),
        dfp.AssertColExists(*"NAME Pop Biden2020".split()),
        dfp.RenameCols({'NAME':'name'})
    ]
    votes = dfp.runPipeline(pipeline)
    

    geoms = load_precinct_geoms(geom_file)
    df = pd.merge(votes, geoms, on='name', how='right')
    df = df.fillna(0)
    return df


def load_precinct_geoms(geom_file=None):
    if geom_file is None:
        geom_file = os.path.join(HOME, 'data/precinct_geoms/BaCoPrecinct-wgs84.shp')

    tasks = [
        LoadGeoms(geom_file),
        dfp.SelectCols('NAME', 'geoms'),
        dfp.RenameCols({'geoms': 'geom', 'NAME':'name'})
    ]
    geoms = dfp.runPipeline(tasks)
    return geoms


def load_precinct_demographics(fn=None):
    if fn is None:
        fn = os.path.join(HOME, "data/precinct_data/precinct_race_data.csv")
        
    df = pd.read_csv(fn, index_col=0)
    
    #TODO, find source of duplicates and remove them
    df = df.groupby('name').tail(1)
    return df


class LoadGeoms(dfp.AbstractStep):
    def __init__(self, fn):
        self.fn = fn
        
    def apply(self, df):
        return fgeom.load_geoms_as_df(self.fn)

    

def plat_shape(shapes, labels=None, fontdict=None, buffer_deg=0, **kwargs):
    """Plat the outliners of the requested shapes on the map
    
    Inputs
    ----------
    shapes
        (list) list of geometries to plot 
    
    Optional Inputs
    -----------------
    labels
        (list) List of labels to put on each shape. Default is
        no labels.
    fontdict
        (dict) Control how the labels are displayed
    buffer_deg
        (float) Dilate or erode the shapes for better presentation
        Use negative values to erode.
    """
    
    try:
        shapes = shapes.values 
    except AttributeError:
        pass 

    try:
        labels = labels.values 
    except AttributeError:
        pass 
    
    default_fontdict = dict(
        fontsize = 16,
        backgroundcolor='w',
    )
    
    if fontdict is None:
        fontdict = default_fontdict
    else:
        default_fontdict.update(fontdict)
        fontdict = default_fontdict
    
    if buffer_deg != 0:
        shapes = npmap(lambda x: x.Buffer(buffer_deg), shapes)

    #idebug()
    for i in range(len(shapes)):
        fplots.plot_shape(shapes[i], **kwargs)

    if labels is not None:
        assert len(labels) == len(shapes)
        for i in range(len(shapes)):
            shp = shapes[i]
            centroid = shp.Centroid()
        
            plt.text(centroid.GetX(), centroid.GetY(), labels[i], fontdict=fontdict, clip_on=True)
    
    ax = plt.gca()
    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])


from tqdm import tqdm
def compute_frac_overlaps(big_geoms, small_geoms):    
    """Compute the fraction of each small geometry that overlaps each of the big_geoms.
    
    Given a small number of big_geoms, and a large number of small_geoms,
    computing the fractional overlap of each one is, in principle, an
    O(nm) task, where n > m. This function uses an rtree to speed up
    the process considerably. 
    
    There is no constraint that len(big_geoms) > len(small_geoms), but
    the code does run faster that way.
    
    Inputs
    ---------
    big_geoms
        (list) A (short) list of geometries of length N
    small_geoms
        (list) A (longer) list of geometries of length M
        
    Returns
    ----
    A 2d numpy array of shape (N,M). the value at i,j is the fraction
    of the area of small_geoms[j] that lies inside big_geoms[i]
    """
    index = create_index(small_geoms)
    #idebug()
    
    out = np.zeros( (len(big_geoms), len(small_geoms)) )
    for i in tqdm(range(len(big_geoms))):
        big = big_geoms[i]
        env = big.GetEnvelope()
        indices = list(index.intersection(env))
        
        for j in indices:
            frac = overlap(small_geoms[j], big)
            out[i, j] = frac
    
    #Doesn't work because I can't pickle geometries!
    #from frm.parmap import parmap
    #fargs = dict(index=index, small_geoms=small_geoms)
    #out = parmap(_compute_frac, big_geoms, fargs=fargs, engine='multi')
    #out = np.array(out)
    return out


def plotEnv(env, *args, **kwargs):
    x0, x1, y0, y1 = env
    x = [x0, x1, x1, x0, x0]
    y = [y0, y0, y1, y1, y0]
    plt.plot(x, y, *args, **kwargs)


def create_index(geoms):
    index = rtree.index.Index(interleaved=False)

    for i, g in enumerate(geoms):
        if g.IsEmpty():
            env = [0,0,0,0]
        else:
            env = g.GetEnvelope()
        index.insert(i, env)
    return index    


def overlap(geomA, geomB):
    """Measures the fraction of geomA that is within geomB"""
    
    inter = geomA.Intersection(geomB)

    #plt.clf()
    #idebug()
    #fplots.plot_shape(geomB, 'k-', label="Geom B")
    #fplots.plot_shape(geomA, 'r-', label="Geom A", lw=4)
    #fplots.plot_shape(inter, 'b-', label="Intersection")
    #plt.legend()
    #plt.pause(1)

    #print("*\n"*5)
    #print(inter.GetGeometryName())
    if inter.GetGeometryName() in ['POINT', 'MULTILINESTRING']:
        #print("foo")
        return 0
    
    overlap_area = inter.Area()
    if overlap_area == 0:
        return 0
    
    frac = overlap_area / geomA.Area()
    return frac
    
 
