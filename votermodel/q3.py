from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import scipy.optimize as spOpt
import frm.plots as fplots
import pandas as pd
import numpy as np
import common

import votermodel.utils as utils 

    
"""
Calculates the interesting values for all DEM candidates, i.ie
the fraction of day-of-in-person voters from each party that voted
for each candidate.

"""

def main():

    votersByPrecinct = utils.loadNumVotersByPrecinct()
    votes = common.loadElectionResultsByPrecinct(2018, primary=False)

    votes = votes[votes.Party == 'DEM']
    
    df = votes.groupby('Candidate').apply(fit, votersByPrecinct).reset_index(drop=True)
    return df
    
def fit(df, votersByPrecinct):
    candidate = df.Candidate.iloc[0]
    votesWon = utils.computeVotesWon(df, candidate)
    res = utils.solveForVoterShare(votersByPrecinct, votesWon, 'NumVoters')

    assert res.success
    coeffs = res.x 
    out = pd.DataFrame()
    out['candidate'] = [candidate]
    out['DF'] = coeffs[0]
    out['RF'] = coeffs[1]
    out['IF'] = coeffs[2]

    return out 
    
