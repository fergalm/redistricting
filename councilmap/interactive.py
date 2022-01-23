
import matplotlib.pyplot as plt


class InteractivePlot(object):
    """An interactive plot
    Clicking in the plot activates a requested function which can
    interact with the data.

    See exampleInteractivePlot() in this file
    """
    def __init__(self, state):
        self.state = state
        
        f = plt.gcf()

        self.updateEvent = 'key_press_event'
        f.canvas.mpl_disconnect(self.updateEvent)
        f.canvas.mpl_connect(self.updateEvent, self)

        ax = plt.gca()
        pc = self.state['plot_controller']
        osm = pc.inventory['osm'] 
        ax.callbacks.connect('xlim_changed', osm.render())
        ax.callbacks.connect('ylim_changed', osm.render())

        pc.render()

    def __del__(self):
        self.disconnect()

    def __call__(self, event):
        if not event.inaxes:
            return

        x = event.xdata
        y = event.ydata
        key = event.key
        pc = self.state['plot_controller']
        self.process_event(pc, x, y, key)
        pc.render()

    def process_event(self, pc, x, y, key):
        if key.upper() == 'U':
            pc.inventory['osm'].render()
        elif key.upper() == 'B':
            pc.inventory['black_pop'].toggle()
        else:
            pass 
        
    def disconnect(self):
        """Disconnect the figure from the interactive object

        This method is called by the destructor, but Python
        doesn't always call the destructor, so you can do so
        explicitly.         And probl should
        """
        print ("Disconnecting...")
        plt.gcf().canvas.mpl_disconnect(self.updateEvent)
        plt.gca().callbacks.disconnect('xlim_changed')
        plt.gca().callbacks.disconnect('ylim_changed')



##
## Some toy data
#x_seq = [x / 100.0 for x in xrange(1, 100)]
#y_seq = [x**2 for x in x_seq]

##
## Scatter plot
#fig, ax = plt.subplots(1, 1)
#ax.scatter(x_seq, y_seq)

##
## Declare and register callbacks
#def on_xlims_change(event_ax):
    #print "updated xlims: ", event_ax.get_xlim()

#def on_ylims_change(event_ax):
    #print "updated ylims: ", event_ax.get_ylim()

#ax.callbacks.connect('xlim_changed', on_xlims_change)
#ax.callbacks.connect('ylim_changed', on_ylims_change)

##
## Show
#plt.show()
