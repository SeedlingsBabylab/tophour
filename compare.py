import sys
import os
import csv

import pandas as pd


top_basic = pd.read_csv("top_bl_hours.csv")
top_lena = pd.read_csv("data/06_07_topregions.csv")

top_basic["closest_lena"] = 0
top_basic["close_lena_overlap"] = 0

all_bl = pd.read_csv("data/all_basiclevel.csv",
                     dtype={"subj": str, "month": str})

file_overlap_ratios = []

results = []


for name, top_bl in top_basic.groupby(by="file"):
    top_l = top_lena.query("file == \"{}\"".format(name))
    lena_bins = []
    bl_bins = []

    for i, row in top_l.iterrows():
        idx = row["orig_index"]
        lena_bins.extend(range(idx, idx+60, 5))

    lena_bins.sort()

    for i, row in top_bl.iterrows():
        idx = row["onset"]
        bl_range = range(idx, idx + 60, 5)
        overlap = 0
        for x in bl_range:
            if x in lena_bins: overlap += 1
        results.append([name, idx, row['num_words'], overlap])
        bl_bins.extend(bl_range)
    bl_bins.sort()
    total_overlap = 0

with open("region_overlaps.csv", "wb") as out:
    writer = csv.writer(out)
    writer.writerow(["file", "bl_onset", "num_words", "lena_overlap"])
    writer.writerows(results)


results = []
for name, top_bl in top_basic.groupby(by="file"):
    top_l = top_lena.query("file == \"{}\"".format(name))
    lena_bins = []
    bl_bins = []
    print name
    file_bl = all_bl.query(
        "SubjectNumber == \"{}\" & audio_video == \"audio\"".format(name))

    res = []

    for i, row in top_l.iterrows():
        idx = row["orig_index"]

        lena_range = range(idx, idx + 60, 5)
        lena_bins.extend(lena_range)

        ms_onset = idx * 5 * 60 * 1000
        reg = file_bl.query("onset >= {} & offset <= {}".format(
            ms_onset, ms_onset + 3600000))

        res.append([name, idx, reg.shape[0]])

    for i, row in top_bl.iterrows():
        idx = row["onset"]
        bl_range = range(idx, idx + 60, 5)

        overlap = 0
        lena_idx = res[i % 5][1]
        lena_bins = range(lena_idx, lena_idx + 60, 5)
        for x in bl_range:
            if x in lena_bins:
                overlap += 1

        res[i % 5].extend([idx, row["num_words"], overlap])
    results.extend(res)


with open("compare_region_overlaps.csv", "wb") as out:
    writer = csv.writer(out)
    writer.writerow(["file", "lena_onset", "lena_wordcount",
                     "bl_onset", "bl_wordcount", "overlap"])
    writer.writerows(results)


results = []
for name, top_bl in top_basic.groupby(by="file"):
    top_l = top_lena.query("file == \"{}\"".format(name)).iloc[0]
    top_b = top_bl.iloc[0]

    results.append([name, top_b['onset']*5*60*1000, "ms", "bl"])
    results.append([name, top_l['orig_index']*5*60*1000, "ms", "lena"])




with open("top_hour_bl_vs_lena.csv", "wb") as out:
    writer = csv.writer(out)
    writer.writerow(["file", "onset", "time", "bl_lena"])
    writer.writerows(results)
# print
