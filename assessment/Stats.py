#!/usr/bin/env python

import os
import sys
from collections import defaultdict
from matplotlib import pyplot as py

'''
   Returns back a precision-recall curve (in .png format), 
   given a file with prec-rec data

   It also calculates the coverage of the predictions supplied,
   to be added as an extra piece of information in the plot

'''


def calc_cov(prec_list, rec_list):

    cov_list = []
    pred_cov = 0
    for i in range(0,len(prec_list)-1):
        prec_count = prec_list[i]
        rec_count = rec_list[i]
        cov_list.append(float(prec_count)/float(rec_count))

    pred_cov = max(cov_list)
    return round(pred_cov, 2)


def plot_roc_curve(pr,rec, filename, pred_cov, f_score, ont):

    pname = filename + '_' + ont + '.png'

    ax = py.figure()
    py.plot(rec, pr, 'r')
    py.xlabel('Recall')
    py.ylabel('Precision')
    py.title('Precision-Recall curve for ' + ont)
    py.axis([0,1,0,1])
    f_score = round(float(f_score),2)
    pred_cov = round(float(pred_cov),2)
    text_box = 'F-Measure = %0.2f\nCoverage = %0.2f' %(f_score,pred_cov)
    box_props = dict(boxstyle="round,pad=0.3", fc="orange")
    py.text(0.98,0.98,text_box, fontsize=11, ha='right', va='top', bbox=box_props)
    ax.savefig(pname)

if __name__ == '__main__':
    list1 = []
    list2 = []
    calc_cov(list1, list2)
