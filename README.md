# generating the top lena hours 
#### (i.e. data/06_07_topregions.csv):

```
$ python compare_subsamplers.py data/lena5min data/06_07_topregions.csv 5
```

# generating the top basic_level hours:
#### (i.e. data/top_bl_hours.csv)

```
$ python top.py data/all_basiclevel.csv data/06_07_topregions.csv
```


# generating the top hour csv's:

```
$ python compare.py
```

compare.py will generate these files:

### top_hour_bl_vs_lena.csv

This is the top ranked hour for each 06/07 audio file under two metrics:

- Highest average CTC/CVC value reported by LENA
- Greatest number of words in our own sparse_code.csv files
    - chunked by hour, with onsets starting every 5 minutes 


### compare_region_overlaps.csv

These are the top 5 regions ranked by the same 2 metrics described above. The associated word count in any given region is also reported. The 'overlap' column reports the degree of overlap between the two 1 hour regions in each row (basic_level vs. lena, where overlap is the number of shared 5 minute bins). The top 5 for each file is ranked relative to the basic_level metric (going from highest ranked to lowest in each group of 5 for each file).


### region_overlaps.csv

Reports the number of 5 min bin overlap between the bl regions and lena regions.
This is overlap between each bl region and all potential lena regions, not just the region it's paired up with as a function of rank (as in compare_region_overlaps.csv).

In other words, if any of a given bl region's 5 min bins overlaps with **any** of the 5 hours worth of lena 5 min bins, it will count as an overlap.