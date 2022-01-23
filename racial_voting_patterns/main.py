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
Calcuate the vote fraction achieved by Black/non-Black gubanatorial
candidates as a function of how many Black people in the precinct

Check race of all candidates
Play with Indian candidate

Plot number of black people against number of democratic voters


I've been doing a little work on the question of race-based voting 
patterns, I wanted to share something. 

The attached plot shows the fraction of votes achieved in each precinct by Black candidates in the 2018 Gubernatorial Primary, compared to the
fraction of the precinct that identifies as "White Alone" in the 2020 census. There is a clear trend that Black candidates did worse in majority white precincts than they did majority white precincts.

However, the trend is less strong than I expected. Even in the whitest precincts, the black candidates still claimed an average of 70% of the votes, and at least 60% of the votes all precincts.

Now, this is not an apples to apples comparison. Just because 50% of a precinct is white does not mean that 50% of the votes in the Democratic primary were also white. In all likelihood very few Black voters are registered Republican, and I have no idea what the racial distribution of primary voters is.

I'm going to play with this a bit more before releasing it, so please don't distribute widely. And if you have any ideas as to how I might make a more compelling chart, do let me know
"""

def load():
    print("Loading Precinct race data")
    precinct = common.load_vote_data_by_precinct()
    cb = common.load_census_blocks()
    print("Computing   precinct demographics...")
    precinct_race_data = computePrecinctRaceData(precinct, cb)
    
    print("Loading Voter roll")
    vr = common.load_voter_rolls(2021)
    idx = vr.Party.isin(['DEM', 'REP'])
    vr.loc[~idx, 'Party'] = 'IND'
    
    vr = vr.groupby(['Precinct', 'Party']).County.count().reset_index()
    vr = vr.rename({'County':'NumReg'}, axis=1)
    return precinct_race_data, vr 


def main2018(*args):
    
    precinct_race_data, vr = args 
    precinct_race_data = precinct_race_data.copy()
    
    #Load data
    #votes = common.loadElectionResultsByPrecinct(2018, primary=True)
    #race = load2018PrimaryCandidates()
    votes = common.loadElectionResultsByPrecinct(2018, primary=False)
    race = load2018GeneralCandidates()
    votes = countVotesByCandidateRace(votes, race)

    def measureDemFrac(row):
        idx = row.Party == 'DEM' 
        demFrac = np.sum(row[idx].NumReg) / (np.sum(row.NumReg) + 1e-99)
        return demFrac 
    
    demFrac = vr.groupby('Precinct').apply(measureDemFrac).to_frame('DemFrac')
    precinct_race_data = pd.merge(precinct_race_data, demFrac, left_on='name', right_index=True)
    
    #Merge
    df = pd.merge(precinct_race_data, votes, left_on='name', right_on='Precinct')
    
    #Plot
    return df


def main2014(*args):
    
    precinct_race_data, vr = args 
    precinct_race_data = precinct_race_data.copy()
    
    #Load data
    votes = common.loadElectionResultsByPrecinct(2014, primary=False)
    race = load2014CeCandidates()
    votes = countVotesByCandidateRace(votes, race)

    def measureDemFrac(row):
        idx = row.Party == 'DEM' 
        demFrac = np.sum(row[idx].NumReg) / (np.sum(row.NumReg) + 1e-99)
        return demFrac 
    
    demFrac = vr.groupby('Precinct').apply(measureDemFrac).to_frame('DemFrac')
    precinct_race_data = pd.merge(precinct_race_data, demFrac, left_on='name', right_index=True)
    
    #Merge
    df = pd.merge(precinct_race_data, votes, left_on='name', right_on='Precinct')
    
    #Plot
    return df


def make_plot(df, title):
    plt.clf()
    plot1(df, 'C1', 'r', title)
    plt.xlabel("Percent of Precinct Identifying as White")
    plt.ylabel("Percent of Votes for Black Candidates")
    plt.title(title, fontsize=26)
    fplots.add_watermark()
    
    
def plot_for_debbie(df14, df18g):
    
    plt.clf()
    plot1(df14, 'C1', 'r', label='2014 Primary')
    plt.xlabel("Percent of Precinct Identifying as White")
    plt.ylabel("Percent of Votes for Black Candidates")
    plt.title("Racial Voting in Baltimore County 2014 Primary", fontsize=26)
    fplots.add_watermark()
    plt.savefig('primary2014.png')
    

    plt.clf()
    plot1(df18g, 'C4', 'r', label='2018 General')
    plt.xlabel("Percent of Precinct Identifying as White")
    plt.ylabel("Percent of Votes for Black Candidates")
    plt.title("Racial Voting in Baltimore County 2018 General", fontsize=26)
    fplots.add_watermark()
    plt.savefig('general2018.png')

def plot2(df14, df18):
    plt.figure(3)
    plt.clf()
    resid = plot1(df14, clr='C1', fit='r', label="2014 Primary")
    resid = plot1(df18, clr='C3', fit='r', label="2018 Primary")

    plt.xlabel("Percent of Precinct Identifying as White")
    plt.ylabel("Percent of Votes for Black Candidates")
    fplots.add_watermark()
    fplots.mark_as_draft()
    plt.legend(loc=3)
    plt.xlim([0,100])
    
    plt.figure(2)
    plt.clf()
    cm = plt.cm.RdBu
    import frm.norm as fnorm 
    norm = fnorm.DiscreteNorm(14, -8, 8)
    fplots.chloropleth(resid.geom, resid.resid, cmap=cm, norm=norm)
    plt.axis((-77.1, -76.2, 39.1, 39.8))


def plot1(df, clr, fit, label):
    
    #df['percentWhite'] = 100 * df.WhitePrimaryVoters.values
    #denom = df.WhitePrimaryVoters.values + df.BlackPrimaryVoters.values
    #df['percentWhite'] /= denom 
    df['percentWhite'] = 100 * df.TotalWhite.values / df.TotalPop.values
    
    df = df.sort_values(['isBlack', 'percentWhite'])
    idx = (df.isBlack) * (df.VoteFrac > 0)
    
    x = df.percentWhite[idx].values
    #x = df.DemFrac[idx].values
    s = df.TotalVotes.values
        
    #plt.plot(df.percentBlack[idx], np.arange(np.sum(idx)), 'k-')
    plt.scatter(x, 100 * df.VoteFrac[idx], s=s[idx], 
        c=clr,
        ec='k',
        linewidths=2,
        label=label,
        )
    
    fObj = Lsf(x, 100 * df.VoteFrac[idx], 1, order=2)
    f = fObj.getBestFitModel()
    plt.plot(x, f, '-', color=fit, lw=3)
    
    out = df[idx].copy()
    out['resid'] = fObj.getResiduals()
    return out


def countVotesByCandidateRace(votes, race):
    df = votes #Mneumonic
    #Select only Dem gubanatorial canddidates
    #idx = (df.Office == 'Governor / Lt. Governor') #& (df.Party == 'DEM')
    idx = (df.Office == 'County Executive       ')
    df = df[idx].copy()

    df = pd.merge(df, race, left_on='Candidate', right_on='name')
    df = df.groupby(['Precinct', 'isBlack']).Votes.sum().reset_index()
    
    totalVotes = df.groupby('Precinct').Votes.sum().to_frame('TotalVotes')
    df2 = pd.merge(df, totalVotes, on='Precinct')
    df2['VoteFrac'] = df2['Votes'].values / (df2['TotalVotes'].values + 1e-10)
    return df2


def load2018GeneralCandidates():

    candidates = [
        ('Ben Jealous', True),
        ('Larry Hogan', False), 
    ]
    
    df = pd.DataFrame(candidates, columns=['name', 'isBlack'])
    return df


def load2018CeCandidates():

    candidates = [
        ('John Johnny O Olszewski, Jr.', True),
        ('Al Redmer, Jr.', False), 
    ]
    
    df = pd.DataFrame(candidates, columns=['name', 'isBlack'])
    return df
    
def load2018PrimaryCandidates():

    candidates = [
        ('Alec Ross', False),
        ('Ben Jealous', True),
        ('James Hugh Jones, II', True), 
        ('Jim Shea', False),
        ("Krish O'Mara Vignarajah", True),
        ('Ralph Jaffe', False),  #Check
        ('Rich Madaleno', False),
        ('Rushern L. Baker, III', True),
        ('Valerie Ervin', True),  #aka Kevin Kamentez
    ]
    
    df = pd.DataFrame(candidates, columns=['name', 'isBlack'])
    return df


def load2014PrimaryCandidates():

    candidates = [
        ('Anthony G. Brown', True),
        ('Charles U. Smith', True),
        ('Cindy A. Walsh', False),
        ('Doug Gansler', False),
        ('Heather Mizeur', False),
        ('Ralph Jaffe', False),
    ]
    
    df = pd.DataFrame(candidates, columns=['name', 'isBlack'])
    return df

def load2014GeneralCandidates():

    candidates = [
        ('Anthony G. Brown', True),
        ('Larry Hogan', False),
    ]
    
    df = pd.DataFrame(candidates, columns=['name', 'isBlack'])
    return df


def load2014CeCandidates():

    candidates = [
        ('George H. Harman', False),
        ('Kevin Kamenetz', True),
    ]
    
    df = pd.DataFrame(candidates, columns=['name', 'isBlack'])
    return df
 
 
def computePrecinctRaceData(precinct, cb):
    #Compute precinct/censusblock overlap by area
    overlap = common.compute_frac_overlaps(precinct.geom, cb.geom)
    
    #What properties of each census block should we aggregate at
    #the precinct level
    cols = [
        'TotalPop', 
        'TotalWhite', 
        'TotalBlack', 
        'VotingTotal', 
        'VotingWhite',
        'VotingBlack',
    ]
    
    #Initialise the columns to zero
    for c in cols:
        precinct[c] = 0
    
    

    #Assign demographic valus to precincts
    for i in range(len(precinct)):
        fracs = overlap[i]
        for c in cols:
            precinct.loc[i, c] = np.sum(cb[c].values * fracs)
    
    precinct['BlackPrimaryVoters'] = precinct['TotalBlack'] * .15
    precinct['WhitePrimaryVoters'] = precinct['TotalWhite'] * .10
    return precinct





def loadPrecinctResults(
    year, 
    county="Baltimore", 
    party='Democratic', 
    primary=False, 
    path=None
):
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
