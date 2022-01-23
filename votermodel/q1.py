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
"""

def main():

    votersByPrecinct = utils.loadNumVotersByPrecinct()
    votes = common.loadElectionResultsByPrecinct(2018, primary=False)

    candidates = [
        'Ben Jealous',
        'John Johnny O Olszewski, Jr.',
        #'Alex Foley',
        'Stephen Lafferty',
        #'Robbie Leonard',
        'Larry Hogan',
        'Al Redmer, Jr.',
        #'David Marks',
        'Stephen A. McIntire',
        #'Chris West',
    ]
    #answerType = 'NumReg'  
    answerType = 'NumVoters'
        
    plt.clf()
    for i, cand in enumerate(candidates):
    
        votesWon = utils.computeVotesWon(votes, cand)
        res = utils.solveForVoterShare(votersByPrecinct, votesWon, answerType)

        assert res.success
        coeffs = res.x 
        print(coeffs)
        
        plt.subplot(2, 3, i+1)
        plot(votersByPrecinct, coeffs, votesWon, answerType)
        plt.title(cand)
    fplots.add_watermark()
    plt.suptitle("Day of Election Voting Preferences")
    

def plot(vr, coeffs, votesWon, values='NumVoters'):
    
    mat, _ = utils.constructMatrices(vr, votesWon, values)
    model = np.dot(mat, coeffs)

    #plt.clf()
    plt.plot(model, votesWon.Votes.values,  'ko')
    mx = np.max(model)
    plt.plot([0, mx], [0,mx], color='g', lw=3)
    print(max(model))
    plt.axis('equal')
    
    msg = """
%.0f%% of Reg. Democrats +    
%.0f%% of Reg. Republicans + 
%.0f%% of Reg. Independents
""" %(100*coeffs[0], 100*coeffs[1], 100*coeffs[2])

    fplots.text_at_axis_coords(.05, .6, msg)
    plt.grid()
    
