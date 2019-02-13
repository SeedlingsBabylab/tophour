from batch_subrdict import *
from original_algo import *

import csv
import sys


if __name__ == "__main__":

    start_dir = sys.argv[1]
    # subreg_dict_file = sys.argv[2]
    output_file = sys.argv[2]
    top_n = int(sys.argv[3])

    # file_groups = find_all_file_groups(start_dir)
    file_groups = [FileGroup(os.path.join(start_dir, x), "stuff", "stuff") for x in os.listdir(start_dir) if "lena5min" in x]

    results = {}

    regions = []

    # subregion_dict = read_subr_dict(subreg_dict_file)

    for group in file_groups:
        print group.lena_file
        lena = parse_lena(group.lena_file)
        ranked_regions = rank_regions(lena)
        filtered_ranked_regions = filter_overlaps(ranked_regions, int(top_n))

        original_filtered_ranked = Overlaps(group.lena_file, top_n)
        original_filtered_ranked.find_dense_regions()

        new = filtered_ranked_regions
        old = original_filtered_ranked.tuple_set_from_map(original_filtered_ranked.ranked_ctc_cvc)

        couple = (new, old)

        results[os.path.basename(group.lena_file)[:5]] = {"new": new, "old": old}


    with open(output_file, "wb") as output:
        writer = csv.writer(output)

        ordered_resample = OrderedDict(sorted(results.iteritems()))

        writer.writerow(["file", "region_num",
                         "orig_index", "orig_awc", "orig_ctc", "orig_cvc", "orig_ctc_cvc",
                         "new_index", "new_awc", "new_ctc", "new_cvc", "new_ctc_cvc"])

        for file, samples in ordered_resample.iteritems():
            line = [file, None, None, None, None, None, None, None, None, None, None, None]
            for x in range(top_n):
                line[1] = x + 1

                line[2] = samples["old"][x][0] # orig_index
                line[3] = format(samples["old"][x][4], '.3f') # orig_awc
                line[4] = format(samples["old"][x][2], '.3f') # orig_ctc
                line[5] = format(samples["old"][x][3], '.3f') # orig_cvc
                line[6] = format(samples["old"][x][1], '.3f') # orig_ctc_cvc

                line[7] = samples["new"][x][0]                 # new_index
                line[8] = format(samples["new"][x][4], '.3f')  # new_awc
                line[9] = format(samples["new"][x][2], '.3f')  # new_ctc
                line[10] = format(samples["new"][x][3], '.3f') # new_cvc
                line[11] = format(samples["new"][x][1], '.3f') # new_ctc_cvc

                writer.writerow(line)





    #     new_file = (group.cha_file, filtered_ranked_regions)
    #     new_regions.append(new_file)
    #
    # new_subregion_dicts = []
    # for file in new_regions:
    #     new_subregion_dicts.append(ranked_regions_to_dict(file))