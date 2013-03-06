#!/usr/bin/python

# The assessment program takes in 2 files: One file containing predictions for a set of target proteins and the other file containing the true experimental validations for the same targets

import os
import sys
import re
import argparse
from collections import defaultdict
from matplotlib import pyplot as py


def plot_roc_curve(pr,rec, filename, pred_cov, f_score, ont):

    pname = re.sub('\.[a-z]+','.png',filename)
    pname = ont + '_' + pname

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

def calculate_pred_cov(prec_counts_list, rec_counts_list):
    
    cov_list = []
    pred_cov = 0
    for i in range(0,len(prec_counts_list)-1):
        prec_count = prec_counts_list[i]
        rec_count = rec_counts_list[i]
        cov_list.append(float(prec_count)/float(rec_count))
    
    pred_cov = max(cov_list)
    return round(pred_cov, 2)

def extract_all_proteins(threshold_list,pred_dict):
    
    prots_per_thresh = defaultdict(lambda:set())

    for i in threshold_list:
        i = str(i)
        if i == '1.0':
            i = '1.00'
        if pred_dict.has_key(i):
            for prot in pred_dict[i]:
                prots_per_thresh[prot].update(pred_dict[i][prot])

    return prots_per_thresh

def calculate_precision(pred_annotation, true_annotation, unique_proteins, pred_file, ont):
    
    threshold_range = defaultdict()
    prec_per_thresh = []
    rec_per_thresh = []
    p_count = []
    r_count = []
    f_score = []
    i = 0.01
    filename = pred_file.split('_')[0] + '_prec_rec_values.txt'
    ofile_handle = open(filename, 'w')

    while i <= 1.01:
        threshold_range[i] = 1
        i = i + 0.01

    thresh_keys = threshold_range.keys()
    thresh_keys.sort(reverse=True)

    for thresh in thresh_keys:
        #print '%0.2f' % thresh
        total_prec_per_thresh = 0
        total_rec_per_thresh = 0
        prec_count = 0
        threshold_list = set()
        rec_count = len(true_annotation)

        for new_threshold in thresh_keys:
            if float(thresh) <= float(new_threshold):
                threshold_list.add(float(new_threshold))
        
        prots_per_thresh = extract_all_proteins(threshold_list, pred_annotation)
                
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
        print >> ofile_handle, str(thresh) + '\t' + str(avg_prec) + '\t' + str(avg_rec)
        p_count.append(prec_count)
        r_count.append(rec_count)
        try:
            f_score.append(float((2*(avg_prec)*(avg_rec)) / (avg_prec + avg_rec)))
        except:
            f_score.append(0.0)
    
    pred_cov = calculate_pred_cov(p_count, r_count)
    F_measure = max(f_score)
    plot_roc_curve(prec_per_thresh, rec_per_thresh, pred_file, pred_cov, F_measure, ont)

def parse_prediction_file(pred_file, ontology):
    go = defaultdict()
    if ontology == 'F': 
        mfo_file_handle = open('list_of_molecular_function_terms.txt','r')
        for data in mfo_file_handle:
            corr_data = re.sub(r'\n','',data)
            go[corr_data] = 1

        pred_annotation = defaultdict(lambda:defaultdict(lambda:set()))
        file_handle = open(pred_file, 'r')
        for lines in file_handle:
            fields = re.sub(r'\n','',lines).split('\t')
            if go.has_key(fields[1]):
                pred_annotation[fields[2]][fields[0]].add(fields[1])

    elif ontology == 'P':
        bpo_file_handle = open('list_of_biological_process_terms.txt','r')
        for data in bpo_file_handle:
            corr_data = re.sub(r'\n','',data)
            go[corr_data] = 1
        
        pred_annotation = defaultdict(lambda:defaultdict(lambda:set()))
        file_handle = open(pred_file, 'r')
        for lines in file_handle:
            fields = re.sub(r'\n','',lines).split('\t')
            if go.has_key(fields[1]):
                pred_annotation[fields[2]][fields[0]].add(fields[1])
    
    return pred_annotation

def parse_exp_file(exp_file, ontology):
    go = defaultdict()

    if ontology == 'F':
        mfo_file_handle = open('list_of_molecular_function_terms.txt','r')
        for data in mfo_file_handle:
            corr_data = re.sub(r'\n','',data)
            go[corr_data] = 1
        
        true_annotation = defaultdict(lambda:set())
        unique_proteins = defaultdict()

        file_handle = open(exp_file, 'r')
        for lines in file_handle:
            fields = re.sub(r'\n','',lines).split('\t')
            if go.has_key(fields[1]):
                unique_proteins[fields[0]] = 1
                true_annotation[fields[0]].add(fields[1])

    elif ontology == 'P':
        bpo_file_handle = open('list_of_biological_process_terms.txt','r')
        for data in bpo_file_handle:
            corr_data = re.sub(r'\n','',data)
            go[corr_data] = 1
        
        true_annotation = defaultdict(lambda:set())
        unique_proteins = defaultdict()

        file_handle = open(exp_file, 'r')
        for lines in file_handle:
            fields = re.sub(r'\n','',lines).split('\t')
            if go.has_key(fields[1]):
                unique_proteins[fields[0]] = 1
                true_annotation[fields[0]].add(fields[1])
    
    return true_annotation, unique_proteins


print "Welcome to the CAFA Assessment Tool!!!!"
print "*************************************************"

parser = argparse.ArgumentParser(prog='assess_prediction.py',description='Asseess the predictions produced through different prediction methods')

parser.add_argument('--PFile',action='store',help='Specifies the path to a file containing predictions from a specific method. The file needs to follow the required format to be accepted by the software.')
parser.add_argument('--BFile',action='store' ,help='Specifies the path to a file containing true experimental validations for the target proteins. This can be a simple tab delimited file with 2 columns, the first column is the protein identifier and second column contains the GO term.')
parser.add_argument('--Ont',action='store',nargs='+',default='all',help='Provide a choice as to what type of ontology would the user like to assess. In the default event, assessment of both ontologies will be provided')
parser.add_argument('--Prop',action='store',default=False,help='Mention whether the input prediction file has predictions propagated to the root or not. By default, it is assumed that the predictions are unpropagated.Set to False')

args = parser.parse_args()

# Check for valid arguments

if not args.PFile == '': 
    pred_file = args.PFile
else:
    print "Please submit a valid prediction file"
    sys.exit(1)

if not args.BFile == '':
    exp_file = args.BFile
else:
    print "Please submit a valid Benchmark File. If you do not have a benchmark created, use the CAFA Benchmark Creation Tool to create a benchmark first and then run this script."
    sys.exit(1)

# Check for Propagation status

if args.Prop == 'True':
    os.system("""python propagate_predictions.py """ + pred_file)
    input_file = pred_file.split('_')[0] + '_prediction_propagated.txt'
    os.system("""python map_to_swiss_prot_id.py """ + input_file)
    infile = input_file.split('_')[0] + '_prediction_with_SP_id.txt'
    os.system("""python extract_benchmark_predictions.py """ + infile)
    prediction_file = infile.split('_')[0] + '_pred_set.txt'
else:
    os.system("""python map_to_swiss_prot_id.py """ + pred_file)
    infile = pred_file.split('_')[0] + '_prediction_with_SP_id.txt'
    os.system("""python extract_benchmark_predictions.py """ + infile)
    prediction_file = pred_file[0] + '_pred_set.txt'

# Check file formats

pred_file_handle = open(prediction_file, 'r')
for lines in pred_file_handle:
    fields = re.sub(r'\n','',lines).split('\t')
    
    if lines.startswith('END'):
        continue
    if not len(fields) == 3:
        print 'Incorrect file format.Please check and submit again.'
        sys.exit(1)
    if not re.match('GO:\d+',fields[1]) and re.match('\d\.\d+',fields[2]):
        print 'Problems with values in some fields.Please check and submit again.'
        sys.exit(1)

print 'Finished checking prediction file for format.'

exp_file_handle = open(exp_file, 'r')
for line in exp_file_handle:
    fields = re.sub(r'\n','',line).split('\t')
    
    if not len(fields) == 2:
        print 'Incorrect file format.Please check and submit again.'
        sys.exit(1)
    if not re.match('GO:\d+',fields[1]) :
        print 'Problems with values in some fields.Please check and submit again.'
        sys.exit(1)

print 'Finished checking experimental file for format.'

# Store ontology information

user_ontology = args.Ont

if len(user_ontology) == 1:
    
    if user_ontology[0] == 'F':
        pred_annotation_mfo = parse_prediction_file(prediction_file, user_ontology[0])
        [true_annotation_mfo, unique_proteins_mfo] = parse_exp_file(exp_file, user_ontology[0])
        calculate_precision(pred_annotation_mfo, true_annotation_mfo, unique_proteins_mfo, prediction_file, user_ontology[0])
    
    elif user_ontology[0] == 'P':
        pred_annotation_bpo = parse_prediction_file(prediction_file, user_ontology[0])
        [true_annotation_bpo, unique_proteins_bpo] = parse_exp_file(exp_file, user_ontology[0])
        calculate_precision(pred_annotation_bpo, true_annotation_bpo, unique_proteins_bpo, prediction_file, user_ontology[0])

elif(user_ontology) == 2:    
    if user_ontology[0] == '' or user_ontology[1] == '':
        print 'Missing value for the ontology argument'
        sys.exit(1)
    
    pred_annotation_mfo = parse_prediction_file(prediction_file, 'F')
    [true_annotation_mfo, unique_proteins_mfo] = parse_exp_file(exp_file, 'F')
    calculate_precision(pred_annotation_mfo, true_annotation_mfo, unique_proteins_mfo, prediction_file, 'F')

    pred_annotation_bpo = parse_prediction_file(prediction_file, 'P')
    [true_annotation_bpo, unique_proteins_bpo] = parse_exp_file(exp_file, 'P')
    calculate_precision(pred_annotation_bpo, true_annotation_bpo, unique_proteins_bpo, prediction_file, 'P')

else:
        pred_annotation_mfo = parse_prediction_file(prediction_file, 'F')
        [true_annotation_mfo, unique_proteins_mfo] = parse_exp_file(exp_file, 'F')
        calculate_precision(pred_annotation_mfo, true_annotation_mfo, unique_proteins_mfo, prediction_file, 'F')

        pred_annotation_bpo = parse_prediction_file(prediction_file, 'P')
        [true_annotation_bpo, unique_proteins_bpo] = parse_exp_file(exp_file, 'P')
        calculate_precision(pred_annotation_bpo, true_annotation_bpo, unique_proteins_bpo, prediction_file, 'P')

