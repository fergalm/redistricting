from ipdb import set_trace as idebug
import scipy.optimize as spOpt
import pandas as pd
import numpy as np
import warnings
import common


def compute_vote_excess(candidate, doipPerPrecinct, votesWon):

    votes = votesWon[votesWon.Candidate == candidate]
    assert len(votes) > 0
    #idebug()
    
    df = fit(votes, doipPerPrecinct) 

    actual_votes = votes["Precinct Votes".split()].reset_index(drop=True)
    
    model_votes = compute_model_votes(doipPerPrecinct, df)
    df = pd.merge(actual_votes, model_votes, on='Precinct')
    df['vote_excess'] = df['Votes'] - df['expected_votes']
    df['frac_excess'] = df['vote_excess'] / (1+df.expected_votes)
    
    #idebug()
   
    geoms = common.load_vote_data_by_precinct()
    geoms = geoms['name geom'.split()]
    df = pd.merge(df, geoms, left_on='Precinct', right_on='name')
    return df


def fit(df, votersByPrecinct, initGuess=None):
    """Private function of compute_vote_excess"""
        
    candidate = df.Candidate.iloc[0]
    votesWon = computeVotesWon(df, candidate)
    res = solveForVoterShare(votersByPrecinct, votesWon, 'NumVoters', initGuess=initGuess)

    out = pd.DataFrame()
    out['candidate'] = [candidate]

    if res.success:
        coeffs = res.x 
        out['DF'] = coeffs[0]
        out['RF'] = coeffs[1]
        out['IF'] = coeffs[2]
        out['cost'] = res.fun
    else:
        out['DF'] = -1
        out['RF'] = -1
        out['IF'] = -1
        out['cost'] = -1

    return out 


def compute_model_votes(votersByPrecinct, frac):
    """Private function of compute_vote_excess"""
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


def loadNumVotersByPrecinct(fn=None):
    """Load the number of voters from each party who
    cast a vote on the day of election.
    
    Similar numbers for early voters do not seem to
    be available from the BoEl
    """
    warnings.warn("Deprecated. Use common.load_DOIP_voters_by_precinct() instead")
    
    if fn is None:
        fn = "/home/fergal/data/elections/MdBoEl/Baltimore/turnout2018BalCo.csv"
    
    df = pd.read_csv(fn)
    df['PRECINCT'] = df.PRECINCT.str[1:]
    
    #Pivot to get election day numbers. I can't find
    #votes per candidate for the early voting data
    df = df.pivot(index='PRECINCT', columns='PARTY', values='POLLS')

    df2 = pd.DataFrame()
    df2['Precinct'] = df.index
    df2['DEM'] = df.DEMOCRAT.values
    df2['REP'] = df.REPUBLICAN.values
    df2['IND'] = (df.GREEN + df.LIBERTARIAN + \
                 df['OTHER PARTIES']  + df.UNAFFILIATED).values
    return df2 


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
    Amat, bVec = constructMatrices(numVoters, votesWon, values)
    
    #idx = bVec > 100
    #Amat = Amat[idx] 
    #bVec= bVec[idx] 
    
    def f(x):
        y = np.dot(Amat, x)
        y = (bVec - y)**2
        return np.sqrt(np.sum(y))

    if initGuess is None:
        initGuess  = [.9, .5, .5]

    bounds = [ [0,1] ] * 3
    res = spOpt.minimize(f, initGuess, method='L-BFGS-B', bounds=bounds)
    assert res.success
    return res


def constructMatrices(vr, votes, values='NumVoters'):
    """Private functio of solveForVoterShare()"""
    df = pd.merge(vr, votes, on='Precinct')
    
    Amat = df[ ['DEM', 'REP', 'IND'] ].values.astype(float)
    Amat[ np.isnan(Amat)] = 0
    
    bVec = df['Votes'].values.astype(float)    
    return Amat , bVec


def computeVotesWon(votes, candidate):
    """Filter the election result table for a single candidate
    
    Inputs
    ------
    votes
        (Dataframe) Dataframe returned by
        `common.loadElectionResultsByPrecinct`. These
        are results for day-of voting
    candidate
        (str) Name of candidate to filter solveForVoterShare
        
    Returns
    ---------
    A dataframe with columns Precinct and Votes
    """

    votesWon = votes[votes.Candidate == candidate].reset_index()
    assert len(votesWon) > 0
    votesWon = votesWon[ ['Precinct', 'Votes'] ]
    return votesWon


def get_countywide_cands(df, party):
    """Get a list of county wide candidates"""
    assert set(df.columns) >= set("Candidate Precinct Party".split())

    df = df[df.Party==party]

    num_precinct = len(set(df.Precinct))
    count = df.groupby('Candidate').Precinct.count()
    idx = count == num_precinct 
    return count[idx].index
