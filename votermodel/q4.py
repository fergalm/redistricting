from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import scipy.optimize as spOpt
import frm.plots as fplots
import pandas as pd
import numpy as np
import common

import votermodel.utils as utils 
import frm.mapoverlay as fmo
    
"""
Where does the model over/under perform across the county
for a given candidate?
"""

def compute_vote_excess(candidate):

    votersByPrecinct = utils.loadNumVotersByPrecinct()
    votes = common.loadElectionResultsByPrecinct(2014, primary=False)
    #idx = votes.Precinct == '08-026'
    #votes = votes[~idx].copy()

    #candidate = 'Robbie Leonard'
    #candidate ='John Johnny O Olszewski, Jr.'
    #candidate = 'Peter Franchot'
    #candidate ='Ben Jealous'
    votes = votes[votes.Candidate == candidate]
    assert len(votes) > 0
    #idebug()
    
    df = fit(votes, votersByPrecinct) 

    actual_votes = votes["Precinct Votes".split()].reset_index(drop=True)
    
    model_votes = compute_model_votes(votersByPrecinct, df)
    df = pd.merge(actual_votes, model_votes, on='Precinct')
    df['vote_excess'] = df['Votes'] - df['expected_votes']
    df['frac_excess'] = df['vote_excess'] / (1+df.expected_votes)
    
    #idebug()
   
    geoms = common.load_vote_data_by_precinct()
    geoms = geoms['name geom'.split()]
    df = pd.merge(df, geoms, left_on='Precinct', right_on='name')
    return df


def fit(df, votersByPrecinct):
    candidate = df.Candidate.iloc[0]
    votesWon = utils.computeVotesWon(df, candidate)
    res = solveForVoterShare(votersByPrecinct, votesWon, 'NumVoters')
    #idebug() 
    
    print(res.fun)
    assert res.success
    coeffs = res.x 
    print(coeffs)
    out = pd.DataFrame()
    out['candidate'] = [candidate]
    out['DF'] = coeffs[0]
    out['RF'] = coeffs[1]
    out['IF'] = coeffs[2]

    return out 


def solveForVoterShare(numVoters, votesWon, values='NumReg', initGuess=None):
    """Compute the average fraction of voters in each
    party that voted for a candidate averaged over
    precincts.
    
    Inputs
    ---------
    numVoters
        (Dataframe) Output of `loadNumVotersByPrecinct()`
        This is the number of voters of each party and
        precinct that showed up to vote.
        
    votesWon
        (Dataframe) Output of `computeVotesWon()`, the total
        number of votes won by the candidate in each
        precinct
        
    Returns
    ----------
    A `scipy.optimize.OptimizeResult` object.
    """
    Amat, bVec, total = constructMatrices(numVoters, votesWon, values)
    
    #idx = bVec > 100
    #Amat = Amat[idx] 
    #bVec= bVec[idx] 
    
    def f(x):
        y = np.dot(Amat, x)
        y = (bVec - y)**2
        return np.sqrt(np.sum(y))

    #if initGuess is None:
        #initGuess  = [.9, .5, .5, 0]

    #bounds = [ [0,1] ] * 4
    #bounds[-1] = [-1000, 1000]

    if initGuess is None:
        initGuess  = [.9, .5, .5]

    bounds = [ [0,1] ] * 3
    #bounds[-1] = [-1000, 1000]

    #bounds = None
    res = spOpt.minimize(f, initGuess, method='L-BFGS-B', bounds=bounds)
    assert res.success
    return res


def constructMatrices(vr, votes, values='NumVoters'):
    """Private functio of solveForVoterShare()"""
    df = pd.merge(vr, votes, on='Precinct')
    
    df.to_csv('spreadsheet.csv')
    df['dummy'] = 1 
    #Amat = df[ ['DEM', 'REP', 'IND', 'dummy'] ].values.astype(float)
    Amat = df[ ['DEM', 'REP', 'IND'] ].values.astype(float)
    Amat[ np.isnan(Amat)] = 0
    
    bVec = df['Votes'].values.astype(float)

    #Bit of an expt.
    total = Amat[:, :3].sum(axis=1)
    for i in range(3):
        Amat[:,i] /= total.astype(float)
    bVec /= total.astype(float)
    
    return Amat , bVec, total

#####################################################################

import frm.norm as fnorm 
def plot_vote_excess(df):    
    plt.clf()
    cmap = plt.cm.RdBu
    norm = fnorm.DiscreteNorm(9, -20, 20)
    
    #import matplotlib.colors as mcolor 
    #norm = mcolor.BoundaryNorm([-20, -10, -5, 5, 10, 20], 6)
    
    plt.axis([-77, -76.3, 39.1, 39.8])
    fmo.drawMap()

    ax = plt.subplot(121)
    plt.axis([-77, -76.3, 39.1, 39.8])
    fmo.drawMap()

    idx = np.ones(len(df), dtype=bool)
    #idx = np.fabs(df.excess_votes < .05)
    #fplots.chloropleth(
        #df[idx].geom, df[idx].vote_excess, 
        #cmap=cmap,
        #vmin=-400,
        #vmax=400
    #)
    fplots.chloropleth(
        df[idx].geom, 100 * df[idx].frac_excess, 
        cmap=cmap,
        norm=norm,
        #vmin=-20,
        #vmax=20
    )
    ##add_labels(df[idx].geom, df[idx].Precinct)

    plt.subplot(122)
    plt.plot(df.expected_votes, df.vote_excess, 'ko')
    
    x = np.linspace(1, 1000, 10)
    x = df.expected_votes.sort_values()
    percent = .01*x
    #idebug()
    plt.fill_between(x, -5*percent, 5*percent, color='blue', alpha=.2)
    plt.fill_between(x, -10*percent, 10*percent, color='blue', alpha=.2)
    plt.axhline(0, color='r')
    plt.ylabel("Votes - Expected Votes")
    plt.xlabel("Expected Votes")
    fplots.add_watermark()
    
    idx = df.frac_excess > 4
    print(df[idx])
    return df


def compute_precinct_demographics():
    pct = common.load_precinct_geoms()
    tracts = common.load_census_tracts()
    overlap = common.compute_frac_overlaps(tracts.geom, pct.geom)

    #nT * nT*nP
    pct['VotingTotal'] = np.dot(tracts.VotingTotal.values, overlap)
    pct['VotingBlack'] = np.dot(tracts.VotingBlack.values, overlap)
    pct['VotingWhite'] = np.dot(tracts.VotingWhite.values, overlap)
    return pct
    
    
def decompose_by_race(votes, demo):
    """An attempt to see if I could predict the number of votes
    Ben Jealous gets based on the number of Black and White residents
    in a precinct. The correlation is pretty poor
    """
    
    df = pd.merge(votes, demo, on='name')
    cols = "Precinct Votes expected_votes vote_excess frac_excess VotingTotal VotingBlack VotingWhite".split()
    df = df[cols]

    nb = df.VotingBlack.values
    nw = df.VotingWhite.values
    no = df.VotingTotal.values - nb - nw
    offset = np.ones_like(nb)

    plt.clf()
    plt.plot(df.VotingTotal, df.Votes, 'ko')
    plt.plot([0, 1000], [0, 1000], 'g-')
    plt.plot([0, 100], [0, 1000], 'g-')
    
    Amat = np.vstack([nb, nw, no, offset]).transpose()
    Amat = Amat[:,:-1]
    bVec = df.Votes.values
    
    def f(x):
        y = np.dot(Amat, x)
        y = (bVec - y)**2
        return np.sqrt(np.sum(y))

    bounds = [ [0,1] ] * 3
    #bounds[-1] = [-1000, 1000]
    initGuess  = [.1, .1, .1] #, 0]
    res = spOpt.minimize(f, initGuess, method='L-BFGS-B', bounds=bounds)
    assert res.success
    
    model = np.dot(Amat, res.x)
    plt.clf()
    plt.plot(bVec, model, 'ko')
    plt.plot([0, 1000], [0, 1000], 'g-')
    return res


    

def plot_vote_excess_against_demo(votes, demo):
    
    df = pd.merge(votes, demo, on='name')
    cols = "Precinct Votes expected_votes vote_excess frac_excess VotingTotal VotingBlack VotingWhite".split()
    
    df = df[cols]
    blackFrac = df.VotingBlack.values / df.VotingTotal.values
    whiteFrac = df.VotingWhite.values / df.VotingTotal.values
    nonBlackFrac = 1 - blackFrac

    x = whiteFrac
    plt.clf()
    plt.plot(x, df.Votes, 'ko')
    plt.plot(x, df.vote_excess, 'ro')
    plt.plot(x, df.expected_votes, 'bo')
    plt.axhline(0, color='c')
                   

    

    
def compute_model_votes(votersByPrecinct, frac):
    demFrac = frac.DF.iloc[0]
    repFrac = frac.RF.iloc[0]
    indFrac = frac.IF.iloc[0]
    
    model = pd.DataFrame()
    model['Precinct'] = votersByPrecinct.Precinct 
    
    model['expected_votes'] = \
        demFrac * votersByPrecinct.DEM + \
        repFrac * votersByPrecinct.REP + \
        indFrac * votersByPrecinct.IND 
    return model


def add_labels(shapes, labels, fontdict=None):
    assert len(shapes) == len(labels)
    
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
        backgroundcolor='grey',
    )
    
    if fontdict is None:
        fontdict = default_fontdict
    else:
        default_fontdict.update(fontdict)
        fontdict = default_fontdict
    
    for i in range(len(shapes)):
        shp = shapes[i]
        centroid = shp.Centroid()
    
        plt.text(centroid.GetX(), centroid.GetY(), labels[i], fontdict=fontdict, clip_on=True)
    
