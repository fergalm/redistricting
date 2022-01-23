from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import frmplots.plots as fplots
import pandas as pd
import numpy as np
import common

import votermodel.utils as utils 
from frmbase.support import lmap 
import frmplots.plots as fplots
import frmplots.norm as fnorm
import frmplots.galaxyplot as fgp
import frmgis.plots as fgplots

import re

def main():
    year = 2018
    candidate = "Ben Jealous"
    #candidate = "Brian E. Frosh"
    #candidate = "Peter Franchot"

    plot(year, candidate)
    plt.savefig(f"votermodel/fig3_{year}_{despace(candidate)}.png")

    year = 2014
    candidate = "Anthony G. Brown"
    #candidate = "Brian E. Frosh"
    #candidate = "Peter Franchot"
    plot(year, candidate)
    plt.savefig(f"votermodel/fig3_{year}_{despace(candidate)}.png")



def plot(year, candidate):
    plt.figure(year)
    votesWon = common.loadElectionResultsByPrecinct(year, primary=False)
    doipPerPrecinct = common.load_DOIP_turnout_by_precinct(year, fn=None)

    assert np.all(np.isfinite(votesWon.Votes))
    df = utils.compute_vote_excess(candidate, doipPerPrecinct, votesWon)

    val = df.frac_excess * 100
    lim = np.max(np.fabs(val))
    lim =100
    plt.clf()
    plt.gcf().set_size_inches((10,8))   
    norm = fnorm.DiscreteNorm(11, -lim, lim  )
    _, cb = fgplots.chloropleth(df.geom, val, cmap=plt.cm.PRGn, norm=norm )
    cb.set_label("Performance Relative\nto Model (%)", fontsize=22)
    plt.axis([-76.99, -76.27, 39.2, 39.73])
    ax = plt.gca()
    title = f"{year} ({candidate})"
    plt.title(title, fontsize=26)
    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])
    fplots.add_watermark()
    return df

    
def despace(name):
    return re.subn("\s", "_", name, 0)[0]
