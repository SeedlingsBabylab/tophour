import csv

class Overlaps:

    def __init__(self, lena_file, top_n):
        self.dataset = None
        self.top_n = top_n

        self.meaningful_regions = None
        self.awc_actual_regions = None
        self.ctc_actual_regions = None
        self.cvc_actual_regions = None
        self.ctc_cvc_regions = None

        self.meaningful_map = None
        self.awc_actual_map = None
        self.ctc_actual_map = None
        self.cvc_actual_map = None
        self.ctc_cvc_map = None

        self.ranked_meaningful = None
        self.ranked_awc_actual = None
        self.ranked_ctc_actual = None
        self.ranked_cvc_actual = None
        self.ranked_ctc_cvc = None

        self.load_data(lena_file)

    def load_data(self, file):
        """
        Parses out all the values from the lena file and fills
        the member variables for class Overlaps with all the
        ctc/cvc/awc/etc....values. At the end of the function
        we call find_dense_regions(), which will use all the data
        that was just pulled from the file

        :param file: lena file.
        :return:
        """
        visit_date = None
        with open(file, "rU") as file:
            reader = csv.reader(file)
            reader.next() # skip past the header row
            for line in reader:
                timestamp_split = line[10].split()
                date = timestamp_split[0].split("-")
                time = timestamp_split[1].split(":")

                if visit_date is None:
                    visit_date = (date[0], date[1], date[2])
                elif visit_date != (date[0], date[1], date[2]):
                    print "The timestamps within your file span more than a single day"

                # we represent date/time as a 5d tuple
                # i.e. 02-13-2015 3:35 = (2, 13, 2015, 3, 35)

                # first line of iteration, dataset not instantiated yet
                if self.dataset is None:
                    # instantiate
                    self.dataset = WordDensitySet((date[0],
                                                   date[1],
                                                   date[2],
                                                   time[0],
                                                   time[1]))

                    # add first region magnitude value.
                    # meaningful is represented in seconds.
                    duration_split = line[11].split(":")
                    meaningful_split = line[12].split(":")

                    duration = int(duration_split[0]) * 3600 +\
                               int(duration_split[1]) * 60 +\
                               int(duration_split[2])

                    if duration == 0:
                        duration = 1

                    # meaningful is redefined as ratio between "meaningful" and duration
                    meaningful = float((int(meaningful_split[0]) * 3600 +
                                 int(meaningful_split[1]) * 60 +
                                 int(meaningful_split[2]))) / duration

                    awc_actual = int(line[18])
                    ctc_actual = int(line[21])
                    cvc_actual = int(line[24])

                    self.dataset.data.append((meaningful, awc_actual, ctc_actual, cvc_actual))

                else:
                    # just add to the end of the current dataset

                    duration_split = line[11].split(":")
                    meaningful_split = line[12].split(":")

                    duration = int(duration_split[0]) * 3600 +\
                               int(duration_split[1]) * 60 +\
                               int(duration_split[2])

                    if duration == 0:
                        duration = 1

                    meaningful = float((int(meaningful_split[0]) * 3600 +
                                 int(meaningful_split[1]) * 60 +
                                 int(meaningful_split[2]))) / duration

                    awc_actual = int(line[18])
                    ctc_actual = int(line[21])
                    cvc_actual = int(line[24])

                    self.dataset.data.append((meaningful, awc_actual, ctc_actual, cvc_actual))



            self.find_dense_regions()

    def find_dense_regions(self):
        """
        Here we go through the process of adding up all the
        hour long chunks at offsets of 5 minutes from each other.
        After all the hour chunks have been tallied up and placed
        in their respective member variables, rank_list() is called
        on all of them. rank_list() returns the ranked offsets as well
        as their associated hashmaps.

        :return:
        """
        # we define region in terms of offsets from the beginning
        # so.... regions[n]:
        #
        #           t-begin -> t0 + n*5min
        #
        #           t-end   -> t-begin + 60min (12 x 5)

        regions = [] # each region has an associated tuple (avg-meaningful,
        #                                                   avg-AWC-actual,
        #                                                   avg-CTC-actual,
        #                                                   avg-CVC-actual)

        rank = [] # each rank corresponds to an region (ranked by hour_region average)
        results = []

        x = 0
        y = 12
        hour_buffer = self.dataset.data[x:y]

        while y <= len(self.dataset.data):
            meaningful_sum = 0
            awc_actual_sum = 0
            ctc_actual_sum = 0
            cvc_actual_sum = 0
            ctc_cvc_sum = 0

            for count in hour_buffer:
                meaningful_sum += count[0]
                awc_actual_sum += count[1]
                ctc_actual_sum += count[2]
                cvc_actual_sum += count[3]
                ctc_cvc_sum += float((count[2] + count[3]))/2  # the average between ctc and cvc

            meaningful_ratio = float(meaningful_sum)/12
            awc_actual_ratio = float(awc_actual_sum)/12
            ctc_actual_ratio = float(ctc_actual_sum)/12
            cvc_actual_ratio = float(cvc_actual_sum)/12
            ctc_cvc_ratio = float(ctc_cvc_sum)/12

            regions.append((meaningful_ratio,
                            awc_actual_ratio,
                            ctc_actual_ratio,
                            cvc_actual_ratio,
                            ctc_cvc_ratio))

            # push the buffer slice over to the right by one element
            # and re-slice
            # e.g.:
            #
            #       1 5 4 2 7 5 3 8 0 6 4 3 7 1 6 4 2 9 5 7
            #             \     \
            #              -----
            #               \     \-->
            #                -----

            x += 1  # bump
            y += 1  # bump
            hour_buffer = self.dataset.data[x:y]  # re-slice

        # pull out the N'th index of each element in "regions",
        # which is a list of tuples, with list comprehensions.
        # Each tuple has the average value for the hour chunk
        # at that offset for each ranking metric:
        #
        #   (meaningful, awc, ctc, ctc_cvc)
        #
        self.meaningful_regions = [average[0] for average in regions]

        self.awc_actual_regions = [average[1] for average in regions]

        self.ctc_actual_regions = [average[2] for average in regions]

        self.cvc_actual_regions = [average[3] for average in regions]

        self.ctc_cvc_regions = [average[4] for average in regions]


        self.meaningful_map, self.ranked_meaningful = self.rank_list(self.meaningful_regions, self.top_n)
        self.awc_actual_map, self.ranked_awc_actual = self.rank_list(self.awc_actual_regions, self.top_n)
        self.ctc_actual_map, self.ranked_ctc_actual = self.rank_list(self.ctc_actual_regions, self.top_n)
        self.cvc_actual_map, self.ranked_cvc_actual = self.rank_list(self.cvc_actual_regions, self.top_n)
        self.ctc_cvc_map, self.ranked_ctc_cvc = self.rank_list(self.ctc_cvc_regions, self.top_n)


    def rank_list(self, list, top_n):
        """
        This builds the regions map, resets decimal precision so
        that equality can be checked, and passes the sorted_list,
        region_map, and top_n to the filter_overlaps() method, which
        should run through and check that there are no regions that
        overlap with each other. filter_overlaps will return a
        filtered_list. This filtered list will be returned with the
        region_map (so that we can lookup those regions later.

        :param list: The offset list
        :param top_n: how many subregions to find
        :return: region map and filtered list
        """
        region_map = {}
        ranked_list = []

        list = self.set_precision(list, 7)

        # build the map
        for index, region_average in enumerate(list):
            region_map[index] = region_average

        max = 0
        sorted_list = sorted(list, reverse=True)

        #print "entire list ranked: " + str(sorted(list))
        filtered_list = self.filter_overlaps(sorted_list, region_map, top_n)
        return (region_map, filtered_list)

    def filter_overlaps(self, list, map, top_n):
        """
        This passes through the ranked offset list and uses the region
        map to check that the top_n regions do not overlap with each other.

        :param list: offset list
        :param map: region map
        :param top_n: # of subregions
        :return: a list of offsets (with no overlaps)
        """
        # this is a list of lists, containing interval offsets
        # each inner list corresponds to all offsets containing
        # a certain magnitude
        offset_lists = []

        last_interval = None

        for index, x in enumerate(list):
            # this is the temporary list that will be pushed into the
            # offset lists once its filled
            temp_offsets = []
            for key, value in map.iteritems():
                if value == x:
                    temp_offsets.append(key)
                    last_interval = key
            offset_lists.append(temp_offsets)

        # print "offset list: " + str(offset_lists)
        results = []

        for index, offset_group in enumerate(offset_lists):
            for index, offset in enumerate(offset_group):
                if len(results) >= top_n:
                    break
                if self.overlapping(results, offset):
                    continue
                else:
                    results.append(offset)
                    #last_result = results[len(results)-1]

        # print "results: " + str(results)
        return results

    def overlapping(self, previous_regions, this_start):
        """
        :param previous_regions: all the offsets which have already been added to "results"
        :param this_start: the millisecond starting point of the offset being tested
        :return: True if overlapping, False if not
        """
        for x in previous_regions:
            if (x > (this_start-12)) and (x < (this_start+12)):
                return True
        return False

    def set_precision(self, list, digits):
        """

        :param list: list of averages
        :param digits: number of places after decimal point
        :return: list with precision reset
        """
        factor = 10**digits
        for index, x in enumerate(list):
            temp = int(x * factor)
            temp = float(temp)/factor
            list[index] = temp
        # print "precision reset list: " + str(list)
        return list

    def density_to_time(self, region_map, ranked_list):
        """
        :param region_map: hashtable with index/average as key/value for out of order interval reference
        :param ranked_list: list with top N densest regions in descending order
        :return: list containing the corresponding time intervals
        """

        interval_rank = []

        for x in ranked_list:
            interval_rank.append(region_map[x])

    def tuple_set_from_map(self, indices):
        results = []
        for index in indices:
            entry = (index,
                     self.ctc_cvc_map[index],
                     self.ctc_actual_map[index],
                     self.cvc_actual_map[index],
                     self.awc_actual_map[index])

            results.append(entry)
        return results


class WordDensitySet:

    def __init__(self, time):
        """
        WordDensitySet models the adult word distribution as
        a function of time.
        """
        self.time = time # start time

        # We're going to store tuples of (meaningful, awc.Actual, ctc.Actual, cvc.Actual)
        self.data = []

    def __str__(self):
        return str(self.time) + str(self.data)

    def get(self, time):
        # TODO: fix this. return Unix time conversion
        """

        :param time: 3d tuple representing time (mm, dd, yyyy)
        :return: DensityRegions for that visit
        """

        return self.data[time]

