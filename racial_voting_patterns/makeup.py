from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from frm.anygeom import AnyGeom
from frm.parmap import parmap
import frm.mapoverlay as fmo
import frm.get_geom as fgeom
import frm.plots as fplots
import frm.norm as fnorm
from frm.fitter.lsf import Lsf

from tqdm import tqdm
import common
import time
import os

from frm.support import npmap


"""
Attempts to estimate the racial makeup of the voters

I have the number of registered voters for each party in the precinct
I have the number of black and white people in each precinct

#Reg Dems = a0 * black  + a1*white [+ a2*other]

I use a least squares fit to estimate the parameters [a0, a1].
The predictions match the actual number of per-precinct.

I find the correlation of this model to the data to be pretty good.
Impressive, even, given the crude nature of the model.

I can then filter my voter rolls to just those that vote in 
any one election and repeat the process

Turns out black voters are about 60% of democratic voters regardless of 
whether you're looking at registration, G2018 or P2018
"""

def load():
    vr = common.loadVoterRolls(2021)
    return vr

def main(vr, precincts):
    
    plt.clf()
    ax = plt.subplot(311)
    modelRacialTurnout(vr, precincts, 'reg')
    plt.text(2500, 5800, "Registered Voters", ha='center', fontsize=22)
    
    plt.subplot(312, sharex=ax, sharey=ax)
    modelRacialTurnout(vr, precincts, 'G2018')
    plt.text(2500, 5800, "Voting in 2018 General", ha='center', fontsize=22)
    plt.ylabel("Model Prediction")
    
    plt.subplot(313, sharex=ax, sharey=ax)
    modelRacialTurnout(vr, precincts, 'P2018')
    plt.text(2500, 5800, "Voting in 2018 Primary", ha='center', fontsize=22)
    
    #plt.plot([1, 5000], [1, 5000], 'g-', lw=3)
    plt.subplots_adjust(hspace=0)
    
    plt.xlabel("Num Dems per Precinct")
    fplots.add_watermark()

def modelRacialTurnout(vr, precincts, which):
    
    cnt = count_registered_voters(vr, which)
    cnt = cnt[cnt.Party == 'DEM'].copy()
    cnt = cnt.rename({'LastName':'NumRegDems'}, axis=1)

    precincts = precincts[precincts.isBlack]
    
    df = pd.merge(cnt, precincts, on='Precinct').sort_values('TotalBlack')
    totalWhite = df.TotalWhite.values
    totalBlack = df.TotalBlack.values
    #totalWhite = df.VotingWhite.values
    #totalBlack = df.VotingBlack.values
 
    regDems = df.NumRegDems.values

    
    Amat = np.vstack([totalBlack, totalWhite]).transpose()
    assert Amat.shape[1] == 2
    
    bVec = regDems
    coeffs = np.linalg.lstsq(Amat, bVec, rcond=None)[0]
    

    #plt.plot(totalWhite, 'r-')
    y = coeffs[0] * totalBlack + coeffs[1] * totalWhite
    plt.plot(regDems, y, 'o')
    print("Rms is %.2f" %(np.std(y-regDems)))
    
    msg = r"%.2f $\times$ BlackPop + %.2f $\times$ WhitePop" %(coeffs[0], coeffs[1])
    plt.text(5400, 500, msg, fontsize=18, ha='right')
    plt.plot([0, 5000], [0, 5000], 'g-', lw=3)
    
    #ax = plt.gca()
    #ax.set_xscale('log')
    #ax.set_yscale('log')
    
    return coeffs
    
def count_registered_voters(vr, which='reg'):
    
    if which != 'reg':
        try:
            vr = vr[vr[which]].copy()
        except KeyError:
            raise KeyError("No election called %s in voter roll" %(which))
        
    idx = vr.Party.isin(['DEM', 'REP'])
    vr.loc[~idx, 'Party'] = 'IND'
    gr = vr.groupby(['Precinct', 'Party'])
    cnt = gr.LastName.count().reset_index()
    
    return cnt
    
    
#def formatPrecinct(x):
    #x = str(x)
    #aa = x[:-3]
    #b  = x[-3:]
    
    #try:
        #return "%02i-%s" %(int(aa), b)
    #except ValueError:
        #print("Failed to parse '%s'" % (x))
        #return "00-000"
    
    
