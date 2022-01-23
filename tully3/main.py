
from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import tully3.plotter as plotter
import tully3.interactive as interactive
import tully3.init as init
import common 
import time 


def main(fn):

    state = init.init(fn)

    x = do_something(state)
    #while True:
        #if plotter.is_file_changed(fn):
            #do_something(state)
        #time.sleep(1)
        
def do_something(state):
    plt.clf()
    plt.axis([-76.89, -76.60, 39.21, 39.49])
    
    #x = interactive.InteractivePlot(state)
    #return x
    pc = state['plot_controller']
    pc.render()

    cb = pd.read_csv('tully3/blocks_to_districts.csv')
    rep = state['report_controller']
    print( "\n".join(rep.text(cb)))
                
