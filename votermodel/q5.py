from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import scipy.optimize as spOpt
import frm.plots as fplots
import pandas as pd
import numpy as np
import common

from tqdm import tqdm
import votermodel.utils as utils 
from frm.parmap import parmap 
    
"""
Investigating the robustness of the result to
the initial input seed. 

Conclusion, ~90% of the time, the algorithm converges to the right place
"""

def main():

    votersByPrecinct = utils.loadNumVotersByPrecinct()
    votes = common.loadElectionResultsByPrecinct(2018, primary=False)

    #names = ['David Marks', 'Alex Foley']
    #names = ['Larry Hogan', 'Ben Jealous']
    #names = ['Stephen Lafferty', 'Stephen A. McIntire']
    names = ['Robbie Leonard', 'Chris West']

    idx = votes.Candidate.isin(names)
    votes = votes[idx]
    
    fargs = dict(votes=votes, votersByPrecinct=votersByPrecinct)
    dflist = parmap(run100Sim, np.arange(10), fargs=fargs, engine='multi')
    return pd.concat(dflist)

def run100Sim(itr, votes, votersByPrecinct):
    dflist = []
    
    for i in range(100):
        initGuess = np.random.rand(4)
        initGuess[-1] = 0
        
        gr = votes.groupby('Candidate')
        df = gr.apply(
            fit, 
            votersByPrecinct, 
            initGuess
        ).reset_index(drop=True)
        dflist.append(df)
    return pd.concat(dflist)
    
    
def fit(df, votersByPrecinct, initGuess):
    candidate = df.Candidate.iloc[0]
    votesWon = utils.computeVotesWon(df, candidate)
    res = utils.solveForVoterShare(votersByPrecinct, votesWon, 'NumVoters', initGuess=initGuess)

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
    
