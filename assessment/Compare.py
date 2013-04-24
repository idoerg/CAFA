#!/usr/bin/env python

import os
import sys
from collections import defaultdict
import Stats

def extract_proteins(threshold_list,pred_dict):

    prots_per_thresh = defaultdict(lambda:set())

    for i in threshold_list:
        i = str(i)
        if i == '1.0':
            i = '1.00'
        if pred_dict.has_key(i):
            for prot in pred_dict[i]:
                prots_per_thresh[prot].update(pred_dict[i][prot])

    return prots_per_thresh

def calc(pred_annotation, true_annotation, unique_prots, outfile, ont):
    
    threshold_range = defaultdict()
    prec_per_thresh = []
    rec_per_thresh = []
    p_count = []
    r_count = []
    f_score = []
    i = 0.01
    outfile_handle = open(outfile + '_' + ont , 'w')

    while i <= 1.01:
        threshold_range[i] = 1
        i = i + 0.01

    thresh_keys = threshold_range.keys()
    thresh_keys.sort(reverse=True)

    for thresh in thresh_keys:
        total_prec_per_thresh = 0
        total_rec_per_thresh = 0
        prec_count = 0
        threshold_list = set()
        rec_count = len(true_annotation)

        for new_threshold in thresh_keys:
            if float(thresh) <= float(new_threshold):
                threshold_list.add(float(new_threshold))

        prots_per_thresh = extract_proteins(threshold_list, pred_annotation)

        for protein in prots_per_thresh:
            if true_annotation.has_key(protein):
                prec_count = prec_count + 1

                pred_ann = set()
                true_ann = set()
                true_pos = set()
                false_pos = set()
                false_neg = set()

                pred_ann = prots_per_thresh[protein]
                true_ann = true_annotation[protein]
                true_pos = pred_ann.intersection(true_ann)
                false_pos = pred_ann.difference(true_ann)
                false_neg = true_ann.difference(pred_ann)

                total_prec_per_thresh = total_prec_per_thresh + (float((len(true_pos))) / (float(len(true_pos)) + float(len(false_pos))))
                total_rec_per_thresh = total_rec_per_thresh + (float((len(true_pos))) / (float(len(true_pos)) + float(len(false_neg))))
                
        try:
            avg_prec = float(total_prec_per_thresh) / float(prec_count)
        except:
            avg_prec = 0.0
        try:
            avg_rec = float(total_rec_per_thresh) / float(rec_count)
        except:
            avg_rec = 0.0

        prec_per_thresh.append(avg_prec)
        rec_per_thresh.append(avg_rec)
        print >> outfile_handle, str(thresh) + '\t' + str(avg_prec) + '\t' + str(avg_rec)
        p_count.append(prec_count)
        r_count.append(rec_count)
        try:
            f_score.append(float((2*(avg_prec)*(avg_rec)) / (avg_prec + avg_rec)))
        except:
            f_score.append(0.0)

    pred_cov = Stats.calc_cov(p_count, r_count)
    F_measure = max(f_score)
    Stats.plot_roc_curve(prec_per_thresh, rec_per_thresh, outfile, pred_cov, F_measure, ont)


if __name__ == '__main__':
    calc()
