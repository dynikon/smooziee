#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# peak search from 2d data
###############################################################################

from scipy.signal import argrelmax
import matplotlib.pyplot as plt

class PeakSearch():
    """
    deals with phonon scattering experimental data

        Attributes
        ----------
        x : np.array
            x data
            set by __init__

        y : np.array
            y data
            set by __init__

        name : str
            data name
            set by __init__

        ix_peaks : lst, default None
            indexes recognized as data peaks
            (x[ix_peaks] are the peaks recognized)
            example : [36, 62, 97, ...]

        ix_peakpairs : default None
            indexes recognized as peak pairs
            (x[ix_peakpairs] are the peak pairs recognized)
            example : [[36, 97], [...], ...]

        Notes
        -----
        Indexes in ix_peaks and ix_peakpairs are the indexes counted
        from the minimun data point, NOT FROM THE MINIMUM PEAK POINT.

    """
    def __init__(self, x=None, y=None, name=None, qpoint=None):
        """
        set attributes

        Parameters
        ----------
        x : np.array, default None
            x data

        y : np.array, default None
            y data

        name : str, default None
            data name
            don't have to be set

        qpoint : list of float, default None
            data qpoint
            this is used when you plot figure
        """
        # set attributes
        self.x_data = x
        self.y_data = y
        self.name = name
        self.qpoint = qpoint
        self.ix_peaks = None
        self.ix_peakpairs = None
        self.degenerates = None

    def find_peak(self, order):
        """
        find peak from data automatically

        Parameters
        ----------
        order : int
            threshold to recognize as peak

        Notes
        -----
        1. set ix_peaks

        2. find peak from data_lst
           you can change the value of 'order', which is parameter
           of definition 'scipy.signal.argrelmax'
           see more about 'scipy.signal.argrelmax'
           http://jinpei0908.hatenablog.com/entry/2016/11/26/224216
        """
        extrema = argrelmax(self.y_data, order=order)
        self.ix_peaks = list(extrema[0])
        print("found %s peaks" % len(self.ix_peaks))

    def revise_peak(self, idx, run_mode='test'):
        """
        revise ix_peaks set by find_peak (method)

        Parameters
        ----------
        idx : int or lst
            index you want to add to or remove from ix_peaks

        run_mode : str default 'test'
            choose 'test' or 'run'
              test => This mode is used when you want to find out the index
                      you want to add or remove by making a figure.
                      In this mode, ix_peaks ARE NOT REVISED.
              run => add or remove the index you specify

        Note
        ----
        1. Parameter 'idx' is the index counted
           from the minimun data point, NOT FROM THE MINIMUM PEAK POINT.
        """
        if type(idx) == int:
            idx = [idx]
        if run_mode != 'test' and run_mode != 'run':
            raise ValueError("run_mode must be 'test' or 'run'")

        # set 'add_or_remove'
        add_or_remove = None
        for i in idx:
            if i in self.ix_peaks:
                if add_or_remove == 'add':
                    raise ValueError("Do you want to add peak or remove peak? \
                                      One is in ix_peaks, \
                                      but another is not in ix_peaks")
                add_or_remove = 'remove'
            else:
                if add_or_remove == 'remove':
                    raise ValueError("Do you want to add peak or remove peak? \
                                      One is in ix_peaks, \
                                      but another is not in ix_peaks")
                add_or_remove = 'add'

        # add idx to or remove idx from ix_peaks
        old_ix_peaks = self.ix_peaks.copy()
        if add_or_remove == 'add':
            print("add mode")
            old_ix_peaks.extend(idx)
            old_ix_peaks.sort()
        else:
            print("remove mode")
            for each_idx in idx:
                old_ix_peaks.remove(each_idx)

        if run_mode == 'test':
            print("test")
            fig = plt.figure()
            ax = fig.add_subplot(111)
            self.plot(ax)
            ax.scatter(self.x_data[idx], self.y_data[idx]*1.1,
                       marker="*", c='blue', s=40)
            ax.set_title(self.name+' ('+str(self.qpoint)+')')
            plt.show()
            plt.close()
        else:
            print("set new ix_peaks to self.ix_peaks")
            self.ix_peaks = old_ix_peaks

    def find_peak_pair(self, threshold=6):
        """
        find peak pair from ix_peaks and set ix_peakpairs

            Parameters
            ----------
            threshold : int, default 6
                see Notes

            Returns
            -------
            fruit_price : int
                description

            Notes
            -----
            1. check from lowest peak point whether it has peak pair
            2. if |peak1_x + peak2_x| / 2 < threshold,
               recognize peak1 and peak2 as a pair
        """
        if self.ix_peaks is None:
            raise ValueError("You have to execute find_peak ahead!")

        # condition => stokes anti-stokes
        pairs = []
        flags = []
        for i in range(int(len(self.ix_peaks)/2)+1):
            for j in range(len(self.ix_peaks)-1, i, -1):
                mean = (self.x_data[self.ix_peaks[i]]
                        + self.x_data[self.ix_peaks[j]]) / 2
                if abs(mean) < threshold \
                        and i not in flags and j not in flags:
                    pairs.append(
                      [self.ix_peaks[i], self.ix_peaks[j]])
                    flags.extend([i, j])
        self.ix_peakpairs = pairs
        print("found %s pair" % str(len(self.ix_peakpairs)))

    def revise_peak_pair(self, ix_peakpairs, run_mode='test'):
        """
        revise ix_peakpairs

            Parameters
            ----------
            ix_peakpairs:  lst
                peak pairs you want to make
                  ex) ix_peakpairs = [[36,72], [ , ], ... ]

            run_mode : str default 'test'
                run_mode = 'test' => test (make a figure)
                run_mode = 'run' => set (self.ix_peakpairs = ix_peakpairs)

            Notes
            -----
            Indexes in ix_peakpairs are the indexes counted
            from the minimun data point, NOT FROM THE MINIMUM PEAK POINT.

        """
        # check
        if run_mode != 'test' and run_mode != 'run':
            raise ValueError("run_mode must be 'test' or 'run'")

        if run_mode == 'test':
            cur_ix_peakpairs = self.ix_peakpairs
            self.ix_peakpairs = ix_peakpairs
            fig = plt.figure()
            ax = fig.add_subplot(111)
            self.plot(ax)
            ax.set_title(self.name+' ('+str(self.qpoint)+')')
            plt.show()
            plt.close()
            self.ix_peakpairs = cur_ix_peakpairs
        else:
            self.ix_peakpairs = ix_peakpairs

    def plot(self, ax, run_mode=None):
        """
        plot data

            Parameters
            ----------
            ax : fig.add_subplot
            run_mode : str default None
              run_mode = None or 'raw_data'
              if None, decide from parameters set in attributes
              if 'raw_data', plot raw_data
        """
        # raw data
        ax.scatter(self.x_data, self.y_data, c='red', s=2)
        ax.set_title(self.name+' ('+str(self.qpoint)+')')

        if run_mode == 'raw_data':
            return

        # peak
        if self.ix_peaks is not None:
            if self.ix_peakpairs is None:
                c_lst = ['black' for _ in range(len(self.ix_peaks))]
            else:
                c_lst = ['black' for _ in range(len(self.ix_peaks))]
                color_lst = \
                    plt.rcParams['axes.prop_cycle'].by_key()['color'][3:]
                for i in range(len(self.ix_peakpairs)):
                    for j in self.ix_peakpairs[i]:
                        c_lst[self.ix_peaks.index(j)] = color_lst[i]

            ax.scatter(self.x_data[self.ix_peaks],
                       self.y_data[self.ix_peaks]*1.1,
                       c=c_lst, s=20, marker='v')

        # degenerate
        if self.degenerates is not None:
            for i,(x,y) in enumerate(zip(self.x_data[self.ix_peaks],
                                         self.y_data[self.ix_peaks]*1.1)):
                ax.annotate(str(self.degenerates[i]),(x,y))

    def set_degenerate(self, degenerates):
        """
        set degenerate

            Parameters
            ----------
            degenerates : list of int
                degenerate infomation of each peaks
                  ex) degenerates = [1,1,2,1,2,1,1]
                      these corresponds with each peak point
                      each number corresponds with the number of degenerate
        """
        self.degenerates = degenerates

    def save(self, filename='peak_search.pkl'):
        """
        save object

            Parameters
            ----------
            filename : str, default 'peaksearch.pkl'
              output filename
        """
        def _check_obj(obj):
            if obj is None:
                ValueError("%s is None, please set before save" % obj)

        check_objs = [self.ix_peaks, self.ix_peakpairs, self.degenerates]
        for obj in check_objs:
            _check_obj(obj)
        import joblib
        joblib.dump(self, filename)

def read_peaksearch(filename):
    """
    load peaksearch object dumped by PeakSearch.save(filename)

        Parameters
        ----------
        filename : str
          input filename
    """
    import joblib
    return joblib.load(filename)
