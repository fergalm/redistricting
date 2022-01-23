from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import scipy.optimize as spOpt
import frm.plots as fplots
import pandas as pd
import numpy as np
import common

import votermodel.utils as utils 

    
"""
My proof of concept plot. Compares model prediction
to actual vote share for half a dozen candidates

Do the totals add up to sane values?

Answer is yes, almost always.
Note that for delgates we expect totals to be 1, 2 or 3 depending 
on the district.
"""

def main():

    votersByPrecinct = utils.loadNumVotersByPrecinct()
    votes = common.loadElectionResultsByPrecinct(2018, primary=False)

    #votes.groupby('Office').apply(foo1, votersByPrecinct)

    #do_congress(votes, votersByPrecinct)
    #do_senator(votes, votersByPrecinct)
    do_delegates(votes, votersByPrecinct)
    
def do_senator(votes, votersByPrecinct):
    v1 = votes[votes.Office == 'State Senator          ']
    assert len(v1) > 0
    df = v1.groupby('Legs').apply(state_senate, votersByPrecinct).reset_index()
    gr = df.groupby('District')
    
    for k in ['DF', 'RF', 'IF']:
        print(k, gr[k].sum())


def do_delegates(votes, votersByPrecinct):
    v1 = votes[votes.Office == 'House of Delegates     ']
    assert len(v1) > 0
    df = v1.groupby('Legs').apply(state_senate, votersByPrecinct).reset_index()
    gr = df.groupby('District')
    
    for k in ['DF', 'RF', 'IF']:
        print(k, gr[k].sum())

    
def state_senate(votes, votersByPrecinct):
    return votes.groupby('Candidate').apply(fit, votersByPrecinct, 'Legs')


def do_congress(votes, votersByPrecinct):
    v1 = votes[votes.Office == 'Representative in Congress']
    cong = v1.groupby('Cong').apply(congress, votersByPrecinct).reset_index()
    gr = cong.groupby('District')
    
    for k in ['DF', 'RF', 'IF']:
        print(k, gr[k].sum())

def congress(df, votersByPrecinct):
    return df.groupby('Candidate').apply(fit, votersByPrecinct, 'Cong')
    

def fit(df, votersByPrecinct, district):
    candidate = df.Candidate.iloc[0]
    votesWon = utils.computeVotesWon(df, candidate)
    res = utils.solveForVoterShare(votersByPrecinct, votesWon, 'NumVoters')

    assert res.success
    coeffs = res.x 
    out = pd.DataFrame()
    #out['candidate'] = [candidate]
    out['District'] = [df[district].iloc[0]]
    out['Race'] = district
    out['DF'] = coeffs[0]
    out['RF'] = coeffs[1]
    out['IF'] = coeffs[2]

    return out 
    

