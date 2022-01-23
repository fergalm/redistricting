from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import frmplots.plots as fplots
import pandas as pd
import numpy as np
import common

import votermodel.utils as utils 
from frmbase.support import lmap 
import frmplots.plots as fplots
import frmplots.galaxyplot as fgp


def main():
    plot2018()
    plt.savefig('voteshare2018.png')
    plot2014()
    plt.savefig('voteshare2014.png')

def plot2018():
    year = 2018

    highlight = "Ben Jealous"

    #Filter these candidates from the plots 
    ignoreList = [
        "R. Jay Fisher",
        #"Julie Ensor",
        #"William R. Bill Evans",
        "Arthur M. Frank",
        #"Juliet Fisher",
    ]

    #Offset these name labels
    offsetList = [
        #"John Johnny O Olszewski, Jr.",
        "Scott Shellenberger",
        "Ben Jealous"
    ]


    plot(year, ignoreList, offsetList, highlight)
    
def plot2014():
    year = 2014

    highlight = "Anthony G. Brown"
    
    ignoreList = [
        #"Julie Ensor",
        #"Juliet Fisher",
        "Charles U. Smith",
        "Al Roberts",
        "Arthur M. Frank",
        #"William R. Bill Evans",
        #"Brian E. Frosh",
        "R. Jay Fisher",
        ]
    
    offsetList = [
        #"Juliet Fisher",
        #"Kevin Kamenetz",
        "Anthony G. Brown",
        "Brian E. Frosh",
        #"Scott Shellenberger",
        "Julie Ensor",
    ]
    plot(year, ignoreList, offsetList, highlight)

def plot(year, ignoreList, offsetList, highlight):
    
    votesWon = common.loadElectionResultsByPrecinct(year, primary=False)
    doipPerPrecinct = common.load_DOIP_turnout_by_precinct(year)
    candlist= utils.get_countywide_cands(votesWon, 'DEM')
    
    dflist = lmap(lambda x: fit_for_vote_share(x, doipPerPrecinct, votesWon), candlist)
    perf = pd.concat(dflist)
    perf = perf[perf.DF > 0].sort_values('DF')[::-1]

    print(to_latex(perf))

    perf = perf[~perf.candidate.isin(ignoreList)]
    candlist = perf['candidate'].values
    
    plt.figure(year)
    plt.clf()
    plt.gcf().set_size_inches((10, 8))
    trendPlot(candlist, 100*perf.DF, 100*perf.IF, 100*perf.RF)

    for i, cand in perf.iterrows():
        offset = 0
        if cand.candidate in offsetList:
            offset -= 4
        plt.text(1.7, offset + 100*cand.IF + 1, cand.candidate, ha='center', fontsize=14)
        
    perf = perf[perf.candidate == highlight]
    trendPlot([highlight], 100*perf.DF, 100*perf.IF, 100*perf.RF, clr='r')
                 
    plt.axvspan(.4, 1, color='lightskyblue', zorder=-2)
    plt.axvspan(1.4, 2, color='k', alpha=.1)
    plt.axvspan(2.4, 3,  color='r', alpha=.2)

    ax = plt.gca()
    ax.xaxis.set_ticks([.7, 1.7, 2.7])
    ax.xaxis.set_ticklabels([
        "Vote Share of\nDemocrats",
        "Vote Share of\nIndependents",
        "Vote Share of\nRepublicans"],
        fontsize=22,
    )
    plt.ylabel("Percent of Voters voting for Candidate", fontsize=22)
    plt.title(year, fontsize=28)
    fplots.add_watermark()
    

def trendPlot(labels, *args, **kwargs):
    
    lw = kwargs.pop('lw', 4)
    clr = kwargs.pop('clr', 'grey')
    
    nElt = len(labels)
    nDim = len(args)
    
    data = list(args)
    for i in range(nDim):
        assert len(data[i]) == len(labels)
        try:
            data[i] = data[i].values
        except AttributeError:
            pass 
            
    dx = .4
    for i in range(nElt):
        #clr = "C%i" %(i)
        oldVal = np.nan 
        for j in range(nDim):
            newVal = data[j][i]
            
            if np.isfinite(oldVal):
                plt.plot([j, j+dx], [oldVal, newVal], '-', color=clr, lw=lw)
            h = plt.plot([j+dx, j+1], [newVal, newVal], '-', color=clr, lw=lw)
        
            if j == 0:
                h[0].set_label(labels[i])
            oldVal = newVal
        #return 
        
        
def _plot(x, y, *args, **kwargs):
    x = x.copy()* 100
    y = y.copy() * 100
    plt.plot(x, y, 'ko')
    
    idx = kwargs['candlist'] == 'Ben Jealous'
    assert np.any(idx)
    plt.plot(x[idx], y[idx], 'ro')
    

def fit_for_vote_share(candidate, doipPerPrecinct, votesWon):

    votes = votesWon[votesWon.Candidate == candidate]
    assert len(votes) > 0
    df = utils.fit(votes, doipPerPrecinct) 
    return df


from frmbase.support import npmap 
def to_latex(df):
    df = df.copy()
    for col in "DF RF IF".split():
        df[col] = npmap(lambda x: "%i" %(100*x), df[col])
        
    df.columns = "Candidate Dem Rep Ind cost".split()
    #df = df.drop(["cost"], axis=1)
    return df.to_latex(columns="Candidate Dem Rep Ind".split(), index=False)
