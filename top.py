import pandas as pd
import sys
import os


def top_hour(all_bl, subj, month, n):
    df = all_bl.query(
        "(subj == \"{}\") & (month == \"{}\") & (audio_video == \"audio\")".format(subj, month))
    df = df.sort_values(by=["onset"])
    i = 0
    j = 60
    max = df.offset.max()

    results = []
    while j * 60 * 1000 < max:
        window = df.query("onset >= {} & offset <= {}".format(
            i * 60 * 1000, j * 60 * 1000))
        results.append((i / 5, window.shape[0]))
        i += 5
        j += 5
    results.sort(key=lambda x: x[1], reverse=True)
    return non_overlapping(results, n)


def non_overlapping(regions, n):
    results = []

    def overlap(x):
        for r in results:
            if r[0] - 12 < x[0] < r[0] + 12:
                return True
        return False

    for x in regions:
        if len(results) == n:
            break
        if not overlap(x):
            results.append(x)
    return results


if __name__ == "__main__":
    all_bl = pd.read_csv(sys.argv[1], dtype={"subj": str, "month": str})
    regions = pd.read_csv(sys.argv[2])
    regions["subj"] = regions.file.str[:2]
    regions["month"] = regions.file.str[3:5]

    results = []
    for (subj, month), grp in regions.groupby(by=["subj", "month"]):
        print "{}_{}".format(subj, month)
        ranked = top_hour(all_bl, subj, month, 5)
        results.extend([["{}_{}".format(subj, month)] + list(x)
                        for x in ranked])

    out = pd.DataFrame(results, columns=["file", "onset", "num_words"])
    out.to_csv("top_bl_hours.csv", index=False)
