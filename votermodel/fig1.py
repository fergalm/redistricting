from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import frmplots.plots as fplots
import pandas as pd
import common

import votermodel.utils as utils


def main():
    """Plot raw performance of black and white candidates against racial demograpichis
    """
    
    plt.clf()
    plt.gcf().set_size_inches((10,8))
    plt.subplot(211)
    plot(2014, 'Anthony G. Brown')
    plt.subplot(212)
    plot(2018, 'Ben Jealous')
    
    fplots.add_figure_labels("White Fraction (%)", "Vote Fraction (%)")
    plt.subplots_adjust(hspace=0)
    fplots.add_watermark()
    
    plt.savefig('figure1.png')
    
def plot(year, highlight_candidate):
    df = common.loadElectionResultsByPrecinct(year, primary=False)
    total = compute_total_valid_poll_per_precinct(df)
    df = pd.merge(df, total, on='Precinct')
    df['VoteFrac'] = df.Votes / df.TotalVotes

    race = common.load_precinct_demographics()
    race['BlackFrac'] = race['TotalBlack'] / race['TotalPop']
    race['WhiteFrac'] = race['TotalWhite'] / race['TotalPop']
    race = race[['name', 'BlackFrac', 'WhiteFrac']]
    
    df = pd.merge(df, race, left_on='Precinct', right_on='name')
    df = df.sort_values('WhiteFrac')

    cands = get_countywide_cands(df, 'DEM')

    for c in cands:
        style = dict(
            color='k',
            marker='o',
            alpha=.4, 
            ms=8,
            ls="none",
            lw=4,
        )
        label=None

        if c == highlight_candidate:
            style['color'] = 'r'
            style['ls'] = '-'
            style['alpha'] = 1
            style['marker'] = ','
            label = f"{highlight_candidate} ({year})"
            
        df2 = df[df.Candidate == c]
        plt.plot(100*df2.WhiteFrac, 100*df2.VoteFrac.values, **style, label=label)
    
    plt.legend(loc=1)
    plt.ylim(2, 102)
    return df

def compute_vote_frac(df, candidate):
    df2 = df[df.Candidate == candidate]
    office = df2.Office.iloc[0]
    df3 = df[df.Office==office]

    idebug()
    #merge = pd.merge(df2, total, on='Precinct')
    #merge['vote_frac'] = merge.Votes_x / merge.Votes_y
    
    #cols = "Candidate Office vote_frac".split()
    #return merge[cols].copy()


def get_countywide_cands(df, party):
    return utils.get_countywide_cands(df, party)
    #if party is not None:
        #df = df[df.Party=="DEM"]

    #num_precinct = len(set(df.Precinct))
    #count = df.groupby('Candidate').Precinct.count()
    #idx = count == num_precinct 
    #return count[idx].index


def compute_total_valid_poll_per_precinct(df):
    
    vote_for_many = [
        "Judge of the Circuit Court",
        "Judge Orphans Court",
        "Judge Special Appeals At Large",
        "House of Delegates     ",
    ]
    
    idx = df.Office.isin(vote_for_many)
    df = df[~idx]
    return df.groupby('Precinct').apply(_compute).to_frame('TotalVotes')


def _compute(df):
    return df.groupby('Office').Votes.sum().max()
