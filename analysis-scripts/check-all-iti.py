#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 15:38:35 2020

@author: nolanlem
"""


import numpy as np 
import pandas as pd
import glob 
import matplotlib.pyplot as plt 
import matplotlib.ticker as plticker
import sys
import os
from ast import literal_eval
from io import StringIO
import itertools
from scipy.signal import find_peaks
from collections import defaultdict
import librosa
from scipy.stats import sem
import pandas as pd
import seaborn as sns
sns.set()
os.chdir('/Users/nolanlem/Documents/kura/kura-new-cond/py/')


sr=22050

# def removeStrFormatting(str_array):
#     float_array = [] # array to hold new formatted lists    
#     str_array = [i for i in str_array if i] # remove empty elems
#     for str_arr in str_array:
#         str_arr = str_arr[1:-1] # remove "'[" and "]'"
#         str_arr = str.split(str_arr, ',') # split strings
#         str_arr = [float(elem) for elem in str_arr] # cast each str as float
#         #str_arr = np.array(str_arr, dtype=np.float32) # str to float
#         float_array.append(str_arr)
#     return float_array

def removeStrFormatting(str_array):
    for str_arr in str_array:
        str_arr = str_arr[1:-1] # remove "'[" and "]'"
        str_arr = str.split(str_arr, ',') # split strings
        str_arr = [float(elem) for elem in str_arr] # cast each str as float
        #str_arr = np.array(str_arr, dtype=np.float32) # str to float
    return str_arr


def formFixedBeatBins(wf, thesnd, limitpeaks=False):
    strsnd= os.path.basename(thesnd).split('.')[0]
    beat_bins = 0
    #amp_peaks, _ = find_peaks(wf, height=0.25, distance=sr/3.0) # get amplitude envelope and return peaks
    amp_peaks, _ = find_peaks(wf, height=0.4, distance=sr/2.0) # get amplitude envelope and return peaks
    #print 'numpks %r = %r'%(strsnd, len(amp_peaks))
    avg_int_bb = librosa.samples_to_time(np.average(np.diff(amp_peaks)))
    idealperiods[strsnd] = avg_int_bb     
    
    # get the ideal period from the sound file path
    idealperiod = 60./float(os.path.basename(snd).split('.')[0].split('_')[1])
    fixed_bb = [avg_int_bb*i for i in range(len(amp_peaks))]

    # for vweak case, amp env doesn't work very well 
    # none of the audio should have more than 15 'beats' therefore if find_peaks
    # returns too many peaks, use the 'idealperiod' to create the fixed beat window array
    if limitpeaks==True:
        if len(amp_peaks) > 15:
            print('too many amp peaks')
            fixed_bb = [idealperiod*i for i in range(14)]

    avg_bpm = 60./avg_int_bb # save the avg bpm depending on avg period
    beat_bins = librosa.samples_to_time(amp_peaks) # convert to samples

    # shift over fixed beat window depending on if its > or < first amplitude env peak 
    if fixed_bb[0] < beat_bins[0]:
        fixed_bb += (beat_bins[0] - fixed_bb[0])
    if fixed_bb[0] > beat_bins[0]:
        fixed_bb -= (fixed_bb[0] - beat_bins[0])
    # shift over half window (makes the "GT beat" at 180 deg in phase coherence plots )
    for i in range(1, len(fixed_bb)):
        fixed_bb[i-1] = fixed_bb[i-1] + (fixed_bb[i] - fixed_bb[i-1])/2 
    fixed_bb[-1] = fixed_bb[-1] + avg_int_bb/2. # last in array
    
    if fixed_bb[0] >= avg_int_bb:
        fixed_bb = np.insert(fixed_bb, 0, fixed_bb[0] - avg_int_bb)
    return fixed_bb, avg_bpm, amp_peaks

def flatten2DList(thelist):
    flatlist = list(itertools.chain(*thelist))
    return flatlist

def binBeats(taps, beat_bins):
    taps = np.array(taps)
    digitized = np.digitize(taps, beat_bins) # in secs, returns which beat bin each tap should go into
    bins = [taps[digitized == i] for i in range(1, len(beat_bins)+1)]
    return bins

def binTapsFromBeatWindow(taps):
    binnedtaps = []
    for i, tap in enumerate(taps):
        try:
            binnedtaps.append(taps[i][0]) # take first tap in window
        except IndexError:
            binnedtaps.append(np.nan)
    return binnedtaps
#%%
# A1 no(1,2)        timbre(1,2)
# B1 timbre(1,2)    no(1,2)
# A2 no(3,4)        timbre(3,4)
# B2 timbre(3,4)    no(3,4)
#
pp_dir_A1 = os.path.join('./psychopy','swarm-tapping-study','psychopy-A1')
pp_dir_A2 = os.path.join('./psychopy','swarm-tapping-study','psychopy-A2')
pp_dir_B1 = os.path.join('./psychopy','swarm-tapping-study','psychopy-B1')
pp_dir_B2 = os.path.join('./psychopy','swarm-tapping-study','psychopy-B2')

stim_block_1 = 'block_1/'
stim_block_2 = 'block_2/'

pp_stims = [pp_dir_A1, pp_dir_A2, pp_dir_B1, pp_dir_B2]
blocks = [stim_block_1, stim_block_2]


############## get sndfile strings #####################
sndfiles_no = []
sndfiles_timbre = []

# all the NO_TIMBRE sounds
for snd in glob.glob(os.path.join(pp_dir_A1, stim_block_1, "*.wav")):
    sndfiles_no.append(snd)
for snd in glob.glob(os.path.join(pp_dir_B1, stim_block_2, "*.wav")):
    sndfiles_no.append(snd)
for snd in glob.glob(os.path.join(pp_dir_A2, stim_block_1, "*.wav")):
    sndfiles_no.append(snd)
for snd in glob.glob(os.path.join(pp_dir_B2, stim_block_2, "*.wav")):
    sndfiles_no.append(snd)

# all the TIMBRE sounds
for snd in glob.glob(os.path.join(pp_dir_A1, stim_block_2, "*.wav")):
    sndfiles_timbre.append(snd)
for snd in glob.glob(os.path.join(pp_dir_B1, stim_block_1, "*.wav")):
    sndfiles_timbre.append(snd)
for snd in glob.glob(os.path.join(pp_dir_A2, stim_block_2, "*.wav")):
    sndfiles_timbre.append(snd)
for snd in glob.glob(os.path.join(pp_dir_B2, stim_block_1, "*.wav")):
    sndfiles_timbre.append(snd)


all_snds = [sndfiles_no, sndfiles_timbre]

timbre_conds = ['no', 'timbre']
sync_conds = ['none', 'weak', 'medium', 'strong']
sndfiles = {}

for i, timbre_cond in enumerate(timbre_conds):
    sndfiles[timbre_cond] = {}
    for sync_cond in sync_conds:
        sndfiles[timbre_cond][sync_cond] = {}
        sndfiles[timbre_cond][sync_cond] = [elem for elem in all_snds[i] if os.path.basename(elem).startswith(sync_cond)] 
# now to access all no_timbre sndfiles, e.g. sndfiles_no = sndfiles['no']['none'] + sndfiles['no']['weak'] + ... 
# or like this:
# sndfiles_no_timbre = []
# for sync_cond in sync_conds:
#   sndfiles_no_timbre.extend(sndfiles['no'][sync_cond])

# A1, A2 have all the audio 
versions = ['psychopy-A1/', 'psychopy-A2/']
blocks = ['block_1', 'block_2']
allstim = []
for version in versions:
    for block in blocks:
        for audiofi in glob.glob(os.path.join('psychopy/swarm-tapping-study', version, block, '*.wav')):
            audiofilename = str.split(os.path.basename(audiofi), '.')[0]
            print(audiofilename)
            allstim.append(audiofilename)

allnotimbre = [elem for elem in allstim if str.split(elem,'_')[1] == 'n'] 
alltimbre = [elem for elem in allstim if str.split(elem,'_')[1] == 't']

all_strong = [elem for elem in allstim if str.split(elem,'_')[0] == 'strong']
all_medium = [elem for elem in allstim if str.split(elem,'_')[0] == 'medium']
all_weak = [elem for elem in allstim if str.split(elem,'_')[0] == 'weak']
all_none = [elem for elem in allstim if str.split(elem,'_')[0] == 'none']

n_strong = [elem for elem in allnotimbre if str.split(elem,'_')[0] == 'strong']
n_medium = [elem for elem in allnotimbre if str.split(elem,'_')[0] == 'medium']
n_weak = [elem for elem in allnotimbre if str.split(elem,'_')[0] == 'weak']
n_none = [elem for elem in allnotimbre if str.split(elem,'_')[0] == 'none']

t_strong = [elem for elem in alltimbre if str.split(elem,'_')[0] == 'strong']
t_medium = [elem for elem in alltimbre if str.split(elem,'_')[0] == 'medium']
t_weak = [elem for elem in alltimbre if str.split(elem,'_')[0] == 'weak']
t_none = [elem for elem in alltimbre if str.split(elem,'_')[0] == 'none']


       
#%% # get the csv files 

csvfiles = []
batch_num = 'batch2'
psychopy_batch = ['psychopy-A1','psychopy-A2','psychopy-B1','psychopy-B2']
renamed_batch = 'psychopy/swarm-tapping-study/mturk-csv/' + batch_num + '-renamed/'
participants = []
#versions = ['A1','A2','B1','B2']
#mturk_batches_all = [os.path.join(mturk_batch1_all, version) for version in versions]


# for file in glob.glob(renamed_batch + "*.csv"):
#     print(file)
#     csvfiles.append(file)
#     participants.append(os.path.basename(file).split('.')[0])


for version in ['A1','A2','B1','B2']:
    for file in glob.glob("./psychopy/swarm-tapping-study/mturk-csv/" + batch_num + "-all/" + version + "/*.csv"):
        print(file)
        csvfiles.append(file)
        participants.append(os.path.basename(file).split('.')[0])   
        

#%%

#%% get participant namesfrom csv

subject = []
for csv_file in csvfiles:
    csv_data = pd.read_csv(csv_file, keep_default_na=False)
    batch = os.path.basename(csv_file).split('.')[0].split('_')[2].split('-')[2]
    #print(batch)
    if int(batch) >= 16: # only batch 2
        subject.append(csv_data['Participant Initials'][0])
        
    
for participant in subject:
    subjectplotdir = './psychopy/swarm-tapping-study/analysis-scripts/plots/' + batch_num + '/subjects/' + participant
    if os.path.exists(subjectplotdir) == False:
        os.mkdir(subjectplotdir)    


  
#%%#### get subjects and csvfiles in lists, and make plots dirs for each subject 
# subject = []
# csvfiles = []
# for exp_version in pp_stims:
#     for datafi in glob.glob(os.path.join(exp_version,'data/*.csv')):
#         csvfiles.append(datafi)
#         subjectplot = './psychopy/swarm-tapping-study/analysis-scripts/plots/' + batch_num + '/subjects/' + theperson # make dir for subject's individual plots
#         if os.path.exists(subjectplot) == False:
#             os.mkdir(subjectplot)
        
#%%


#%% ################## FOR NO-TIMBRE TYPE

sync_cond = ['none', 'weak', 'medium', 'strong']
syncbatch = [sndfiles['no']['none'], sndfiles['no']['weak'], sndfiles['no']['medium'], sndfiles['no']['strong']]


idealperiods = {}

sndbeatbins = {}

# load beatbins for no-timbre type
datadirs = ['stim-no-timbre-5', 'stim-timbre-5']
timbre_tags = ['n','t']
stimuli_dirs = ['stimuli_1', 'stimuli_2', 'stimuli_3', 'stimuli_4']
#beatbins_dir = os.path.join(datadir, stimuli_dir, 'phases', 'beat-windows')
#centerbpms_dir = os.path.join(datadir, stimuli_dir, 'phases', 'center-bpm')

sndbeatbins = {}
centerbpms = {}
centerperiods = {}

for datadir, ttag in zip(datadirs, timbre_tags):
    for stimuli_dir in stimuli_dirs:
        beatbins_dir = os.path.join(datadir, stimuli_dir, 'phases', 'beat-windows')
        for fi in glob.glob(beatbins_dir + '/*.txt'):
            fi_basename = str.split(os.path.basename(fi), '.')[0] # --> weak_79_1
            f = str.split(fi_basename, '_') 
            sync_cond = "_".join([f[0], ttag, f[1], f[2]])
            thebeatbins = np.loadtxt(fi, delimiter='\n')
            sndbeatbins[sync_cond] = thebeatbins
        
        centerbpms_dir = os.path.join(datadir, stimuli_dir, 'phases', 'center-bpm')    
        for fi in glob.glob(centerbpms_dir + '/*.txt'):       
            fi_basename = str.split(os.path.basename(fi), '.')[0] # --> weak_79_1
            f = str.split(fi_basename, '_') 
            sync_cond = "_".join([f[0], ttag, f[1], f[2]])    
            thecenterbpm = np.loadtxt(fi)        
            centerbpms[sync_cond] = float(thecenterbpm)
            centerperiods[sync_cond] = 60./float(thecenterbpm)
            

                        
        

#%%
# old code
# for batch in syncbatch:
#     for snd in batch:
#         sndstr = os.path.basename(snd).split('.')[0]
#         wf, sr_ = librosa.load(snd)
#         beat_bins, avg_tempo, _ = formFixedBeatBins(wf, snd)
#         sndbeatbins[snd] = beat_bins
#         idealperiods[snd] = 60./avg_tempo # this is in BPM!!!   

#%% 


#%%
# parse subject taps in csv output files and format into dataframes or arrays

from collections import defaultdict

def removeStrFormatting(str_arr):
    str_arr = str_arr[1:-1] # remove "'[" and "]'"
    str_arr = str.split(str_arr, ',') # split strings
    try:
        str_arr = [float(elem) for elem in str_arr] # cast each str as float
    except ValueError:
        pass
    #str_arr = np.array(str_arr, dtype=np.float32) # str to float
    return str_arr

# default dictionarya

subject_resps = defaultdict(lambda: defaultdict(list))

ordered_subjects = []


block1taps = 'block1_taps.rt'
block2taps = 'block2_taps.rt'
csv_sndfiles = 'sndfile'
csv_tempo = 'tempo'
csv_coupling_cond = 'cond'
csv_version = 'version'
csv_participant = 'Participant Initials'
csv_type = 'type'

condition = []

#### only take good approved csv files #####
subject = []
csvfiles = []
for csv in glob.glob('psychopy/swarm-tapping-study/mturk-csv/batch12-good/*.csv'):
    namestripped = os.path.basename(csv).split('.')[0].split(' ')[0]
    subject.append(namestripped)
    csvfiles.append(csv)

#%%

for csv_file, person in zip(csvfiles, subject):
    print('SUBJECT: ', person)
    df_block = pd.read_csv(csv_file, keep_default_na=False)
    subject_resps[person] = {}  
    
    # get experiment version 
    # experiment_version = os.path.basename(csv_file).split('_')[1]
    # experiment_version = experiment_version.split('-')[1]
    # print(experiment_version)

    try:

        df_block_1 = df_block.get([csv_participant, csv_sndfiles, csv_type, csv_coupling_cond, csv_tempo, csv_version, block1taps])[4:44]
        df_block_2 = df_block.get([csv_participant, csv_sndfiles, csv_type, csv_coupling_cond, csv_tempo, csv_version, block2taps])[44:-1]
        
        df_block_1_type = df_block_1[csv_type]
        #timbre_type = df_block_1['sndfile'].values
    
        for index, row in df_block_1.iterrows():
            sync_cond_version = str.split(os.path.basename(row[csv_sndfiles]), '.')[0]
            subject_resps[person][sync_cond_version] = []
        for index, row in df_block_2.iterrows():
            sync_cond_version  = str.split(os.path.basename(row[csv_sndfiles]), '.')[0]
            subject_resps[person][sync_cond_version] = []
    
        for index, row in df_block_1.iterrows():
            sync_cond_version = str.split(os.path.basename(row[csv_sndfiles]), '.')[0]
            subject_resps[person][sync_cond_version] = removeStrFormatting(row[block1taps])
        for index, row in df_block_2.iterrows():
            sync_cond_version = str.split(os.path.basename(row[csv_sndfiles]), '.')[0]
            subject_resps[person][sync_cond_version] = removeStrFormatting(row[block2taps])
    
    except TypeError:
        print('could not read %r csv file' %(person))
        

        

           
#####NB: subject_resps are now in this format 
#### subject_resps[person][type(no, timbre)][sync_tempo_version]            
        
#%% plot no-timbre taps in line with no-timbre audio 
# NB: this is only for NO-TIMBRE, have to redefine allblocks below 
# since TFA1 only did 'A1' version, we have to isolate the audio from that exp and 
# link it to the taps 

# this is ALL the stimuli for condition 
sndfiles_n_none = sndfiles['no']['none'] 
sndfiles_n_weak = sndfiles['no']['weak']
sndfiles_n_medium = sndfiles['no']['medium']
sndfiles_n_strong = sndfiles['no']['strong']

sndfiles_t_none = sndfiles['timbre']['none'] 
sndfiles_t_weak = sndfiles['timbre']['weak']
sndfiles_t_medium = sndfiles['timbre']['medium']
sndfiles_t_strong = sndfiles['timbre']['strong']

sndfiles_n_none = [os.path.basename(elem).split('.')[0] for elem in sndfiles_n_none]
sndfiles_n_weak = [os.path.basename(elem).split('.')[0] for elem in sndfiles_n_weak]
sndfiles_n_medium = [os.path.basename(elem).split('.')[0] for elem in sndfiles_n_medium]
sndfiles_n_strong = [os.path.basename(elem).split('.')[0] for elem in sndfiles_n_strong]

sndfiles_t_none = [os.path.basename(elem).split('.')[0] for elem in sndfiles_t_none]
sndfiles_t_weak = [os.path.basename(elem).split('.')[0] for elem in sndfiles_t_weak]
sndfiles_t_medium = [os.path.basename(elem).split('.')[0] for elem in sndfiles_t_medium]
sndfiles_t_strong = [os.path.basename(elem).split('.')[0] for elem in sndfiles_t_strong]


sndfiles_n_all = sndfiles_n_none + sndfiles_n_weak + sndfiles_n_medium + sndfiles_n_strong
sndfiles_t_all = sndfiles_t_none + sndfiles_t_weak + sndfiles_t_medium + sndfiles_t_strong


# A1: no_timbre (1,2)   timbre(1,2)


#%%

person = subject[0]

tap_snds_no = list(subject_resps[person].keys())

##%% get all the stimulus names from allstims dir --> allstims list
allstims = []
for fi in glob.glob('./psychopy/swarm-tapping-study/allstims/*.wav'):
    allstims.append(fi)
## allstims is full file path of every stimuli 
#%%#### beat plots per participant #####


#%%

## get all sounds full path for alltimbre and notimbre sound sets 
timbrepaths = []
notimbrepaths = []
for fi in alltimbre:
    timbrepaths.append(os.path.join('./psychopy/swarm-tapping-study/allstims/', fi + '.wav'))
for fi in allnotimbre :
    notimbrepaths.append(os.path.join('./psychopy/swarm-tapping-study/allstims/', fi + '.wav'))

#%%
    
A1_stimuli_names = []
A2_stimuli_names = []
B1_stimuli_names = []
B2_stimuli_names = []

for block in blocks:
    for fi in glob.glob('./psychopy/swarm-tapping-study/psychopy-A1/' + block + "/*.wav"):
        A1_stimuli_names.append(os.path.basename(fi))
    for fi in glob.glob('./psychopy/swarm-tapping-study/psychopy-A2/' + block + "/*.wav"):
        A2_stimuli_names.append(os.path.basename(fi))
    for fi in glob.glob('./psychopy/swarm-tapping-study/psychopy-B1/' + block + "/*.wav"):
        B1_stimuli_names.append(os.path.basename(fi))
    for fi in glob.glob('./psychopy/swarm-tapping-study/psychopy-B2/' + block + "/*.wav"):
        B2_stimuli_names.append(os.path.basename(fi))
#%%

    
subjectplotdir = './psychopy/swarm-tapping-study/analysis-scripts/plots/' + batch_folder + "/subjects/"


# replace all empty trials with [] (tried with np.nan but not good for plotting... )
for person in subject:
    print(person)
    for n, sndfile in enumerate(allstims):
        sync_cond_version = str.split(os.path.basename(sndfile), '.')[0]
    
        try:
            if (subject_resps[person][sync_cond_version] == ['']):
                subject_resps[person][sync_cond_version] = []
        except KeyError:
            print('subject %r did not tap to %r' %(person, sndfile))
#%% PLOT ALL THE SUBJECTS TAPS ON INDIVIDUAL PLOT AND SAVE FIGURE TO DIR of SUBJECT NAME 
thestim2plot = A2_stimuli_names # just stimuli names in 'version'
path2stims = './psychopy/swarm-tapping-study/allstims/'


for cnt, person in enumerate(subject):
    print('.... working on %r %r/%r.....' %(person, cnt, len(subject)))
    plt.figure()
    fig, ax = plt.subplots(len(thestim2plot), 1, sharex=True, sharey=True, figsize=(20,40))
    n = 0
    for j, sndfile in enumerate(sorted(allstims)):
        #print('analyzing', sndfile)
    
        try:
            sync_cond_version = str.split(os.path.basename(sndfile), '.')[0]
            y, sr_ = librosa.load(sndfile)
            subjecttaps = librosa.time_to_samples(subject_resps[person][sync_cond_version]) #need to redefine [(no,timbre)] to look at timbre par exemple
            
            ax[n].plot(y, linewidth=0.5) # plot sound waveform
            ax[n].vlines(subjecttaps, -0.5, 0.5, color='red') # plot subject taps        
            ax[n].vlines(sndbeatbins[sync_cond_version], -0.9, 0.9, color='green') # plot beat bins 
            
            ax[n].set_yticks([]) # turn off y ticks
            ax[n].set_ylabel(sync_cond_version, fontsize=8, rotation=0)
        
            fig.suptitle(person + batch_num + ' taps ')
            n += 1 
        except KeyError:
            pass
            #print('could not find %r' %(sndfile))
    
    plt.savefig(os.path.join(subjectplotdir, person + ' taps.png'), dpi=120)
    plt.close()
    print('\n\n')
    
#%% ACCUMULATE ALL THE SUBJECTS TAPS OVER A SINGLE STIMULI WAVEFORM AND PLOT AND SAVE 
thestim2plot = A2_stimuli_names # just stimuli names in 'version'
path2stims = './psychopy/swarm-tapping-study/allstims/'

markers = ['o', '.', ',', 'x', '+', 'v', '^', '<', '>', 's', 'd','o', '.', ',', 'x', '+', 'v', '^', '<', '>', 's', 'd']

#fig, ax = plt.subplots(len(thestim2plot), 1, sharex=True, sharey=True, figsize=(20,40))


allstrongstims = ['./psychopy/swarm-tapping-study/allstims/' + elem + '.wav' for elem in all_strong]
allmediumstims = ['./psychopy/swarm-tapping-study/allstims/' + elem + '.wav' for elem in all_medium]
allweakstims = ['./psychopy/swarm-tapping-study/allstims/' + elem + '.wav' for elem in all_weak]
allnonestims = ['./psychopy/swarm-tapping-study/allstims/' + elem + '.wav' for elem in all_none]

plt.figure()
fig, ax = plt.subplots(len(allnonestims), 1, sharex=True, sharey=True, figsize=(80,60))


for cnt, person in enumerate(subject[:]):
    print('.... working on %r %r/%r.....' %(person, cnt, len(subject)))
    n = 0
    for j, sndfile in enumerate(sorted(allnonestims[:])):
        #print('analyzing', sndfile)
        
    
        try:
            sync_cond_version = str.split(os.path.basename(sndfile), '.')[0]
            y, sr_ = librosa.load(sndfile)
            subjecttaps = librosa.time_to_samples(subject_resps[person][sync_cond_version]) #need to redefine [(no,timbre)] to look at timbre par exemple
            
            ax[j].plot(y, linewidth=0.5) # plot sound waveform
            ax[j].scatter(subjecttaps, (0.3+0.1*cnt)*1*np.ones(len(subjecttaps)), marker=markers[cnt], s=32) # plot subject taps        
            ax[j].vlines(sndbeatbins[sync_cond_version], -0.9, 3, color='green', linewidth=0.7) # plot beat bins 
            
            ax[j].set_yticks([]) # turn off y ticks
            ax[j].set_ylabel(sync_cond_version, fontsize=8, rotation=0)
        
            fig.suptitle(person + batch_num + ' taps ')
            n += 1 
        except KeyError:
            pass
            #print('could not find %r' %(sndfile))
    
    #plt.savefig(os.path.join(subjectplotdir, person, person + ' taps.png'), dpi=120)
    plt.savefig('/Users/nolanlem/Desktop/allnonetaps.png', dpi=160)
    #plt.close()
    print('\n\n')

plt.close()
#%%%
   

def binBeats(taps, beat_bins):
    taps = np.array(taps)
    digitized = np.digitize(taps, beat_bins) # in secs, returns which beat bin each tap should go into
    bins = [taps[digitized == i] for i in range(1, len(beat_bins)+1)]
    return bins

def binTapsFromBeatWindow(taps):
    binnedtaps = []
    avg_taps_per_bin = []
    for i, tap in enumerate(taps):
        try:
            num_taps_in_bin = len(taps[i])
            avg_taps_per_bin.append(num_taps_in_bin)
            if num_taps_in_bin > 0:            
                random_tap = np.random.randint(low=0, high=num_taps_in_bin)
                binnedtaps.append(taps[i][random_tap]) # take first tap in window
        except IndexError:
            binnedtaps.append(np.nan)
    
    avg_taps_per_stim = np.mean(avg_taps_per_bin)
    return binnedtaps, avg_taps_per_stim
#%% ############# ITI of beat sections 
import scipy.stats

subject_iti_slices = defaultdict(lambda: defaultdict(list))
subject_std_slices = defaultdict(lambda: defaultdict(list))

beatsegments = [(0,5), (5,10), (10,15), (15,20)]
beatstrings = ['0-5', '5-10', '10-15', '15-20']

# no timbre

#slice_to_analyze = sndfiles_n_strong
slice_to_analyze = sndfiles_n_all 

sndfiles_n = [sndfiles_n_none, sndfiles_n_weak, sndfiles_n_medium, sndfiles_n_strong]
sndfile_conds = ['none','weak','medium','strong']

# timbre sndfiles
sndfiles_t = [sndfiles_t_none, sndfiles_t_weak, sndfiles_t_medium, sndfiles_t_strong]


iti = {}
std = {}


### NO TIMBRE!!!
# sndfiles_batch = sndfiles_n
# suptitle_str = 'No Timbre Condition'


### TIMBRE!!!
# sndfiles_batch = sndfiles_t
# suptitle_str = 'Timbre Condition'

#### ALL SOUNDS 

n_none, n_weak, n_medium, n_strong = [],[],[],[]
t_none, t_weak, t_medium, t_strong = [],[],[],[]


for elem in sndfiles['no']['none']:
    n_none.append(os.path.basename(elem).split('.')[0])
for elem in sndfiles['no']['weak']:
    n_weak.append(os.path.basename(elem).split('.')[0])
for elem in sndfiles['no']['medium']:
    n_medium.append(os.path.basename(elem).split('.')[0])
for elem in sndfiles['no']['strong']:
    n_strong.append(os.path.basename(elem).split('.')[0])
    
for elem in sndfiles['timbre']['none']:
    t_none.append(os.path.basename(elem).split('.')[0])
for elem in sndfiles['timbre']['weak']:
    t_weak.append(os.path.basename(elem).split('.')[0])
for elem in sndfiles['timbre']['medium']:
    t_medium.append(os.path.basename(elem).split('.')[0])
for elem in sndfiles['timbre']['strong']:
    t_strong.append(os.path.basename(elem).split('.')[0])

#%%



tn_none = [os.path.basename(elem).split('.')[0] for elem in sndfiles['no']['none'] + sndfiles['timbre']['none']]
tn_weak = [os.path.basename(elem).split('.')[0] for elem in sndfiles['no']['weak'] + sndfiles['timbre']['weak']]
tn_medium = [os.path.basename(elem).split('.')[0] for elem in sndfiles['no']['medium'] + sndfiles['timbre']['medium']]
tn_strong = [os.path.basename(elem).split('.')[0] for elem in sndfiles['no']['strong'] + sndfiles['timbre']['strong']]

all_conds = [tn_none, tn_weak, tn_medium, tn_strong]

#all_conds = [[n_none,n_weak,n_medium,n_strong],[t_none, t_weak, t_medium, t_strong]]

sndfiles_batch = all_conds
suptitle_str = 'Timbre and No Timbre Condition'

#%% ####################################################
# ########### ITI ANALYSIS ############################
########################################################

binned_subject_taps = {}
avg_binned_taps = {}



for person in subject:
    subject_iti_slices[person] = {}
    subject_std_slices[person] = {}
    avg_binned_taps[person] = {}
     
    for sync_cond, sync_str in zip(sndfiles_batch, sndfile_conds):
        iti[sync_str] = []
        std[sync_str] = []
        
        for sync_cond_version in sync_cond:
            binned_subject_taps[sync_cond_version] = []
                    
            try: 
                subject_resps[person][sync_cond_version]
                
                subject_iti_slices[person][sync_cond_version] = []
                subject_std_slices[person][sync_cond_version] = []
                
            except: 
                pass
            
            try:
                taps = subject_resps[person][sync_cond_version]
                sndbeatbin = librosa.samples_to_time(sndbeatbins[sync_cond_version])
                binned_taps = binBeats(taps, sndbeatbin)
                binned_taps, avg_taps_per_bin = binTapsFromBeatWindow(binned_taps)
                #print('%r, %r'%(sync_cond_version, avg_taps_per_bin))
                
                avg_binned_taps[person][sync_cond_version] = avg_taps_per_bin
             
                # these are he realigned taps 
                binned_subject_taps[sync_cond_version].append(binned_taps)
            
                #print(binned_subject_taps)
                
                
            except:
                pass
            
            for beatseg in beatsegments: 
                try:
                    taps = subject_resps[person][sync_cond_version] # get taps for sync_cond_version
                    sndbeatbin = librosa.samples_to_time(sndbeatbins[sync_cond_version]) # get beat bins for sync_cond_version
                    binned_taps = binBeats(taps, sndbeatbin) # bin the taps
                    binned_taps, _ = binTapsFromBeatWindow(binned_taps) # select one tap within each bin
                    
                    normalized_tap_iti = np.diff(binned_taps)/centerperiods[sync_cond_version]
                    tap_iti_slice = normalized_tap_iti[beatseg[0]:beatseg[1]]
                    avg_tap_iti_slice = np.mean(tap_iti_slice) 
                    std_tap_iti_slice = np.std(tap_iti_slice)
                    
                    subject_iti_slices[person][sync_cond_version].append(avg_tap_iti_slice) 
                    subject_std_slices[person][sync_cond_version].append(std_tap_iti_slice)                    
                   #no_timbre_iti.append
                except: 
                    pass
            
            try:
                iti[sync_str].append(subject_iti_slices[person][sync_cond_version])
                std[sync_str].append(subject_std_slices[person][sync_cond_version])
            except:
                pass
            
            #### plot tap density histogram along stimuli waveform
            
            # tap_array = np.array(binned_subject_taps)
            # for i,tap_column in enumerate(tap_array):
            #     vertical_tap_pool = tap_array[:,i]
                
            #     _, bins, _ = plt.hist(vertical_tap_pool, tap_array.shape[1], density=1, alpha=0.5)   

            #     mu, sigma = scipy.stats.norm.fit(vertical_tap_pool) 

            #     best_fit_line = scipy.stats.norm.pdf(bins, mu, sigma)
            #     plt.plot(bins, best_fit_line)
#%%  ########### MAKE CSV for R with mx, std, version 
import csv
csv_data = pd.DataFrame(columns=['subject', 'timbre', 'condition', 'section', 'mx', 'sx'])

sectionstrs = ['start','mid1','mid2','end']

all_conds = [[n_none,n_weak,n_medium,n_strong],[t_none, t_weak, t_medium, t_strong]]

sndfiles_batch = all_conds

with open('./psychopy/swarm-tapping-study/csv/csv-output-rev.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["subject", "version", "condition", "section", "mx", "sx"])
    
    for person in subject:
        subject_sync_cond_arr = {}
        
        iti_subject = {}
        iti_subject[person] = {}
        
        plt.figure()
        fig, ax = plt.subplots(1,1)
        for version_cond in sndfiles_batch:
        
            for sync_cond, sync_str in zip(version_cond, sndfile_conds):
                #print(sync_cond)
                subject_sync_cond_arr[person] = {}
                subject_sync_cond_arr[person][sync_str] = []
                for sync_cond_version in sync_cond:
                    #print(sync_cond_version)
                    try:
                        subject_sync_cond_arr[person][sync_str].append(subject_iti_slices[person][sync_cond_version]) 
                        version = sync_cond_version.split('_')[1]
                        sync_condition = sync_cond_version.split('_')[0]                    
                    except:
                        pass

                
                subject_sync_cond_mx = np.nanmean(np.array(subject_sync_cond_arr[person][sync_str]), axis=0)
                subject_sync_cond_std = np.nanstd(np.array(subject_sync_cond_arr[person][sync_str]), axis=0)                
                
                iti_subject[person]['mx'] = []
                iti_subject[person]['sx'] = []
                for i, mx in enumerate(subject_sync_cond_mx):
                    print(person, version, sync_condition, str(i), subject_sync_cond_mx[i], subject_sync_cond_std[i] )                   
                    writer.writerow([person, version, sync_condition, str(i), subject_sync_cond_mx[i], subject_sync_cond_std[i]])
                    iti_subject[person]['mx'].append(subject_sync_cond_mx[i])
                    iti_subject[person]['sx'].append(subject_sync_cond_std[i])
                           
            
            x_range = np.linspace(0,3,4) # (0, num beat segs -1, num beat segs)
            xticks = [str(elem) for elem in beatstrings]
        
            
            # ax.set_title('Mean ITI per Beat Section')    
            # ax.errorbar(x_range, subject_sync_cond_mx, yerr=subject_sync_cond_std, label=sync_str, marker='.',capsize=3)
    
            
            # plt.setp(ax, xticks=[0,1,2,3], xticklabels=xticks)
            
            # plt.suptitle(suptitle_str)               
            # plt.legend(title='sync conditions', bbox_to_anchor=(1.25, 1))
            # try:
            #     plt.savefig('./psychopy/swarm-tapping-study/mturk-csv/batch12-good/subject-ITIs/' + person + '-ITI.png', dpi=160)
            # except:
            #     os.mkdir('./psychopy/swarm-tapping-study/mturk-csv/batch12-good/' + person + '/')
            
            # plt.savefig('./psychopy/swarm-tapping-study/mturk-csv/batch12-good/subject-ITIs/' + person + '-ITI.png', dpi=160)

#%% make csv for avg beats per bin 
import csv
with open('./psychopy/swarm-tapping-study/mturk-csv/avg-beat-bins-both-cond.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["stimuli", "subject", "average tap in beat bins"])
    for person in subject:
        for sync_cond in sndfiles_batch:
            for sync_cond_version in sync_cond:
                try:
                    writer.writerow([sync_cond_version, person, avg_binned_taps[person][sync_cond_version]])
                except:
                    pass
#%% BEAT BIN AVG TOTALS CSV 

avg_tap_sync_cond = {}

with open('./psychopy/swarm-tapping-study/mturk-csv/avg-beat-bins-totals-subject.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["condition", "subject", "average tap in beat bins"])
    for person in subject:
        for sync_cond, sync_str in zip(sndfiles_batch, sndfile_conds):
            avg_tap_sync_cond[sync_str] = []
            for sync_cond_version in sync_cond:
                try:
                    avg_tap_sync_cond[sync_str].append(avg_binned_taps[person][sync_cond_version])
                    #writer.writerow([sync_cond_version, person, avg_binned_taps[person][sync_cond_version]])
                except:
                    pass
            avg_tap_sync = np.mean(avg_tap_sync_cond[sync_str])
            
            writer.writerow([sync_str, person, avg_tap_sync])

#%% plot histograms of tap densities over waveform stimuli

tap_density_histo = {}
plot_dir = './psychopy/swarm-tapping-study/analysis-scripts/plots/' 


for sync_cond, sync_str in zip(sndfiles_batch, sndfile_conds):
   
    plt.figure()
    fig, ax = plt.subplots(len(sync_cond),1,figsize=(20,40))
    plt.suptitle(sync_str + ' tap density plot')
    
    for n,sync_cond_version in enumerate(sync_cond):
        print('working on %r'%(sync_cond_version))
        try:
            tap_array = np.array(binned_subject_taps[sync_cond_version])
            
            y, _ = librosa.load('./psychopy/swarm-tapping-study/allstims/' + sync_cond_version + '.wav')
            
            beatbins = sndbeatbins[sync_cond_version]
            
            best_fit_contour = []
            
            for i in range(1,tap_array.shape[1]):
                vertical_tap_pool = tap_array[:,i]
                
                #_, bins = np.histogram(vertical_tap_pool, tap_array.shape[1])   
                _, bins = np.histogram(vertical_tap_pool, int(beatbins[i] - beatbins[i-1]))   
            
                mu, sigma = scipy.stats.norm.fit(vertical_tap_pool) 
            
                best_fit_line = scipy.stats.norm.pdf(bins, mu, sigma)
                best_fit_contour.extend(best_fit_line)
                
            
            tap_density_histo[sync_cond_version] = best_fit_contour
            ax[n].plot(best_fit_contour/max(best_fit_contour))
            ax[n].set_ylabel(sync_cond_version, rotation=15)
            ax[n].plot(y)
            
        except:
            pass
    
    plt.savefig(plot_dir + 'tap-density-plots/' + sync_str + ' density plot.png', dpi=160)
    #print(best_fit_line.shape)
    #plt.plot(bins, best_fit_line)

#%%
plt.figure()
y, _ = librosa.load('./psychopy/swarm-tapping-study/allstims/' + sync_cond_version + '.wav')
beatbins = sndbeatbins[sync_cond_version]
plt.plot(y) 
plt.vlines(beatbins,-1,1)
#%%
plt.figure()
fig, ax = plt.subplots(len(thebatch[0]),1)

for sync_cond, sync_str in zip(thebatch, sndfile_conds): 
    for n,sync_cond_version in enumerate(sync_cond):
        try:
            ax[n].plot(tap_density_histo[sync_cond_version])
        except:
            pass

    
#fig, ax = plt.subplots(len(thebatch, 1, sha))

#%%
#####    turn ITI list of lists in DataFrames and take mean 

iti_mean = {}
iti_error = {}
std_mean = {}
std_error = {}

for sync_str in sndfile_conds:
    df = pd.DataFrame(iti[sync_str])
    iti_ = df.mean(axis=0)
    error_ = df.std(axis=0)
    iti_mean[sync_str] = iti_ 
    iti_error[sync_str] = error_
    
    df = pd.DataFrame(std[sync_str])
    iti_ = df.mean(axis=0)
    error_ = df.std(axis=0)
    std_mean[sync_str] = iti_
    std_error[sync_str] = error_

########## plot mean ITI and mean SD of each beat section 
plt.figure()
fig, ax = plt.subplots(2,1,sharex=True) 

x_range = np.linspace(0,3,4) # (0, num beat segs -1, num beat segs)
xticks = [str(elem) for elem in beatstrings]

for sync_str in sndfile_conds:   
    # ax[0].plot(n_iti_mean[sync_str], label=sync_str, marker='.')
    # ax[1].plot(n_stds[sync_str], label=sync_str, marker='.')

    ax[0].set_title('Mean ITI per Beat Section')    
    ax[0].errorbar(x_range, iti_mean[sync_str], yerr=iti_error[sync_str], marker='.', label=sync_str, capsize=3)
    #[ax[0].set_ylim([0.5,1.2])

    
    ax[1].set_title('Mean SD per Beat Section')    
    ax[1].errorbar(x_range, std_mean[sync_str], yerr=std_error[sync_str], marker='.', label=sync_str, capsize=3)
    #ax[1].set_ylim([0.,0.5])

plt.setp(ax, xticks=[0,1,2,3], xticklabels=xticks)

plt.suptitle(suptitle_str)    

plt.legend(title='sync conditions', bbox_to_anchor=(1.05, 1))

#plt.savefig('./psychopy/swarm-tapping-study/analysis-scripts/plots/ITIs/' + suptitle_str + ' ITI.png', dpi=160, bbox_inches='tight')
    
#%%
df_strong = pd.DataFrame(no_timbre_iti['strong'])
iti_strong = df.mean(axis=0)

#%% #########################################################
################### PHASE COHERENCE ##########################
#############################################################


# for sync_cond, sync_str in zip(sndfiles_batch, sndfile_conds):
#     print(sync_str)
#     for sync_cond_version in sync_cond:
#         print('\t', sync_cond_version)
#         for person in subject:
#             print('\t \t', person)
from scipy.interpolate import interp1d


   

def binBeats(taps, beat_bins):
    taps = np.array(taps)
    digitized = np.digitize(taps, beat_bins) # in secs, returns which beat bin each tap should go into
    bins = [taps[digitized == i] for i in range(1, len(beat_bins)+1)]
    return bins

def binTapsFromBeatWindow(taps):
    binnedtaps = []
    avg_taps_per_bin = []
    for i, tap in enumerate(taps):
        try:
            num_taps_in_bin = len(taps[i])
            avg_taps_per_bin.append(num_taps_in_bin)

            if num_taps_in_bin > 1:   
                random_tap = np.random.randint(low=0, high=num_taps_in_bin)
                binnedtaps.append(taps[i][random_tap]) # take first tap in window
            if num_taps_in_bin == 0:
                binnedtaps.append(np.nan)
            if num_taps_in_bin == 1:
                binnedtaps.append(taps[i][0])
        except IndexError:
            binnedtaps.append(np.nan)
    
    avg_taps_per_stim = np.mean(avg_taps_per_bin)
    return binnedtaps, avg_taps_per_stim


binned_taps_per_cond = {}
binned_taps_per_stim = {}  
all_subject_binned_taps_per_stim = {}
    
pc_beat_windows = [(0,4),(4,8),(8,12),(12,16)]

random_color = 255.*np.random.random(80)


for sync_cond, sync_str in zip(sndfiles_batch, sndfile_conds):
    binned_taps_per_cond[sync_str] = []   
    binned_taps_per_stim[sync_str] = {}
    
    f = plt.figure()
    
    fig, ax = plt.subplots(80, 4, subplot_kw=dict(polar=True), gridspec_kw=
                           {'wspace':0.2,'hspace':0.01,'top':0.9, 'bottom':0.1, 'left':0.125, 'right':0.9}, 
                           figsize=(5,80), 
                           sharex=True)
    plt.suptitle('all ' + sync_str + ' stimuli')
    # do these things to all axes in plot
    for ax_ in ax.flat:
        ax_.set_thetagrids([])
        ax_.set_yticklabels([])
        #ax_.set_rticks([])
        ax_.set_axisbelow(True)
        ax_.grid(linewidth=0.1, alpha=1.0)
    
    for n, sync_cond_version in enumerate(sync_cond):    
        all_subject_binned_taps_per_stim[sync_cond_version] = []
        binned_taps_per_stim[sync_str][sync_cond_version] = []        
        subject_binned_taps_per_stim = {}
        
      
        ax[n,0].set_ylabel(sync_cond_version, size=6, rotation=90)
       
        for person in subject:
            print('working on ', person, sync_cond_version)
            try:
                taps = subject_resps[person][sync_cond_version]
                sndbeatbin = librosa.samples_to_time(sndbeatbins[sync_cond_version])
                binned_taps = binBeats(taps, sndbeatbin)
                #print(sndbeatbin)
                #print(binned_taps)
                binned_taps, avg_taps_per_bin = binTapsFromBeatWindow(binned_taps) 
                #print(binned_taps)
                subject_binned_taps_per_stim[person] = []
                
                for i in range(1, len(sndbeatbin)):
                    taptobin = binned_taps[i-1]
                    binmin = sndbeatbin[i-1]
                    binmax = sndbeatbin[i]
                    #print(str(binmin) + '\t' + str(binmax) + '\t taptobin: ' + str(taptobin))
                    bininterp = interp1d([binmin, binmax], [0, 2*np.pi]) #map tap values within window from 0-2pi
                    subject_binned_taps_per_stim[person].append(float(bininterp(taptobin)))
                
                all_subject_binned_taps_per_stim[sync_cond_version].append(subject_binned_taps_per_stim[person])
                        
            except:
                #print('skipping ', person, sync_cond_version)
                pass
            
        
        df_stim = pd.DataFrame(all_subject_binned_taps_per_stim[sync_cond_version])
        
        for m, beatwindow in enumerate(pc_beat_windows):
            beat_column = df_stim.iloc[:, beatwindow[0]:beatwindow[1]].values
            beat_column_pooled_taps = beat_column.flatten()
            
            # calculate phase coherence
            R = np.abs(np.nanmean(np.exp(1j*beat_column_pooled_taps)))
            psi = np.angle(np.nanmean(np.exp(1j*beat_column_pooled_taps)))
            
            randomnoise = np.random.random(len(beat_column_pooled_taps))*0.4
            
            #plt.subplot(1,4,m+1, projection='polar')
            ax[n,m].scatter(beat_column_pooled_taps, 2*np.pi+randomnoise, s=6, alpha=0.75, c=random_color[:len(beat_column_pooled_taps)] )
            ax[n,m].arrow(0, 0.0, psi, 2*np.pi*R, color='black', linewidth=1)            
            # ax[n,m].set_axisbelow(True)
            # ax[n,m].grid(linewidth=0.1, alpha=1.0)            
            # ax[n,m].set_yticklabels([])
            # ax[n,m].set_xticklabels([]) 
            
            # if n==0:
            #     ax[n,m].set_title(str(beatwindow))
    plt.savefig('./psychopy/swarm-tapping-study/analysis-scripts/plots/PCs/'+ 'all-' + sync_str + '.png', dpi=160)



#%% load up phases from .npy files from generative model 
stim_phases = {}
stim_R = {} 
stim_ang = {}

for datadir, ttag in zip(datadirs, timbre_tags):
    for stimuli_dir in stimuli_dirs:
        phases_dir = os.path.join(datadir, stimuli_dir, 'phases', '*.npy')
        R_dir = os.path.join(datadir, stimuli_dir, 'phases', 'pc', '*.txt')
        ang_dir = os.path.join(datadir, stimuli_dir, 'phases', 'ang', '*.txt')
        for fi in glob.glob(phases_dir):
            filen = os.path.basename(fi).split('.')[0]
            filen_split = filen.split('_')
            filen_rev = filen_split[0] + '_' + ttag + '_' + filen_split[1] + '_' + filen_split[2]
            #stim_phases[filen_rev] = np.load(filen)
        for fi in glob.glob(R_dir):
            filen = os.path.basename(fi).split('.')[0]
            filen_split = filen.split('_')
            filen_rev = filen_split[0] + '_' + ttag + '_' + filen_split[1] + '_' + filen_split[2]
            stim_R[filen_rev] = np.loadtxt(filen, delimiter=',')
        
        for fi in glob.glob(ang_dir):
            filen = os.path.basename(fi).split('.')[0]
            filen_split = filen.split('_')
            filen_rev = filen_split[0] + '_' + ttag + '_' + filen_split[1] + '_' + filen_split[2]
            stim_ang[filen_rev] = np.loadtxt(filen, delimiter=',')

#%%

phases = np.load('/Users/nolanlem/Documents/kura/kura-new-cond/py/stim-no-timbre-5/stimuli_1/phases/medium_105_1.npy')


#%%            
            
#plt.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=0.9, wspace=0.2, hspace=0.01)


               
            
                

                        
            
        # df_stim = pd.DataFrame(all_subject_binned_taps_per_stim[sync_cond_version])
        # #print('binned taps per stim',binned_taps_per_stim[sync_str][sync_cond_version])
        # # per subject ... 
        # subject_binned_taps_per_stim = [] 
        # for j in range(len(binned_taps_per_stim[sync_str][sync_cond_version])): # start analyzing beats on 1st window 
        #     # per beat column 
        #     for i in range(1,len(sndbeatbin)):
        #         taptobin = binned_taps_per_stim[sync_str][sync_cond_version][j][i-1]
        #         binmin = sndbeatbin[i-1]
        #         binmax = sndbeatbin[i]
        #         print(str(binmin) + '\t' + str(binmax) + '\t taptobin: ' + str(taptobin))
        #         bininterp = interp1d([binmin, binmax], [0, 2*np.pi]) # interpolate taps wrt beat bin to give value 0-2pi
        #         interpedtaps = bininterp(taptobin)
        #         print(interpedtaps)
        #         subject_binned_taps_per_stim.append(float(interpedtaps))
                
        #     all_subject_binned_taps_per_stim[sync_cond_version].append(subject_binned_taps_per_stim)
        
        # df_stim = pd.DataFrame(all_subject_binned_taps_per_stim[sync_cond_version])
                #print(interpedtaps)
            #circletaps.append(np.array(interpedtaps).mean())
            #alltaps.append(np.array(interpedtaps))    
            
        
        # df_stim = pd.DataFrame(binned_taps_per_stim[sync_str][sync_cond_version])
        
        # average_pc_per_stim = df_stim.mean(axis=0)
        
        # for beat_column in range(df_stim.shape[1]):
        #     df_stim.iloc[:, beat_column]
            
  #%%         
  
fig, ax = plt.subplots(2,1)
ax[0].scatter(np.array([1,2,3]), np.random.random(3))

            
            
            

#%%
for person in subject:
    print(person)
    for sync_cond, sync_str in zip(sndfiles_batch, sndfile_conds):
        print('\t', sync_str)
        for sync_cond_version in sync_cond:
            print('\t \t ', sync_cond_version)
            
        
    
    
    
    









