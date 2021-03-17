import abc
try:
    import elasticsearch6 as es
    import elasticsearch6.helpers as esh
    import elasticsearch6_dsl as dsl
except:
    import elasticsearch as es
    import elasticsearch.helpers as esh
    import elasticsearch_dsl as dsl
import datetime as dt
import dateutil as du

try:
    from ivis import ivis
except:
    class ivis:  # stub for local testing
        elasticsearch = es.Elasticsearch('localhost')


class TsWriter:
    def __init__(self, index_name, ts_field, value_field):
        pass


class TsReader:
    def __init__(self, index_name, ts_field, value_field, from_ts='', to_ts=''):
        self.index_name = index_name
        self.ts_field = ts_field
        self.value_field = value_field

        self.latest_ts = None

        self.from_ts = from_ts
        self.to_ts = to_ts

    def set_latest(self, ts):
        self.latest_ts = ts

    def read(self):
        return self._read()

    def _read(self):
        s = dsl.Search(using=ivis.elasticsearch, index=self.index_name).sort(
            {self.ts_field: 'asc'})

        if self.from_ts:
            s = s.filter('range', **{self.ts_field: {'gte': self.from_ts}})
        if self.to_ts:
            s = s.filter('range', **{self.ts_field: {'lt': self.to_ts}})

        if self.latest_ts:  # query only not yet seen values
            s = s.filter('range', **{self.ts_field: {'gt': self.latest_ts}})

        timestamps = []
        values = []

        batch_size = 10000

        i = 0
        while True:
            res = s[i * batch_size:(i + 1) * batch_size].execute()
            timestamps.extend(map(lambda x: x[self.ts_field], res))
            values.extend(map(lambda x: x[self.value_field], res))

            i += 1
            if len(res) < batch_size:
                break

        if len(timestamps) > 0:
            self.set_latest(timestamps[-1])

        return timestamps, values

# TODO: Old code, needs to be reworked


def estimate_end_ts(first_ts, interval, buckets_count):
    """Estimate end date, such that if you split data between start_ts and end_ts
    with given interval, you get at least (and not significantly more than)
    buckets_count buckets.

    Warning: This is only approximate estimation and end_ts doesn't coincide with a respective
    bucket end!Last bucket should therefore be ignored. """
    try:
        start_date = dt.datetime.strptime(first_ts, pythondateformat)
    except ValueError:
        start_date = dt.datetime.strptime(first_ts, pythondateformat2)

    markers = {
        'y': dt.timedelta(days=365),
        'q': dt.timedelta(days=93),
        'M': dt.timedelta(days=31),
        'w': dt.timedelta(days=8),
        'd': dt.timedelta(hours=26),
        'h': dt.timedelta(minutes=61),
        'm': dt.timedelta(minutes=1),
        's': dt.timedelta(seconds=1),
    }

    num = ''
    mark = ''

    for s in interval:
        if s.isdigit():
            num += s
        else:
            mark += s

    num = int(num)
    delta = markers[mark]

    return start_date+num*buckets_count*delta


esdateformat = "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"
pythondateformat = "%Y-%m-%dT%H:%M:%S.000Z"
pythondateformat2 = "%Y-%m-%dT%H:%M:%S"

# TODO: From old code, neetds to be reworked


class TsAggReader:
    def __init__(self, index_name, ts_field, value_field, agg_interval,
                 agg_method='avg'):
        self.index_name = index_name
        self.ts_field = ts_field
        self.value_field = value_field

        self.agg_method = agg_method
        self.agg_interval = agg_interval

        self.latest_ts = None

    def set_latest(self, ts):
        self.latest_ts = ts

    def read(self):
        def linear_interp(data):  # interpolation of empty buckets
            # there should be no empty buckets on both sides
            for i in range(len(data)):
                if data[i] == None:  # empty bucket
                    # find first non empty bucket
                    j = -1
                    for k in range(i+1, len(data)):
                        if data[k] != None:
                            j = k
                            break
                    # interpolate values between i (inc.) and j (exc.)
                    left = data[i-1]
                    right = data[j]
                    step = (right-left)/(j-i+1)

                    for m in range(i, j):
                        data[m] = data[m - 1] + step

        def get_first_ts(es, index_name, ts_name, start_ts=''):
            query = {'size': 1,
                     'sort': {ts_name: 'asc'}}  # we only need the first record
            if start_ts is None or start_ts == '':
                query['query'] = {'match_all': {}}
            else:
                query['query'] = {}
                query['query']['range'] = {ts_name: {'gte': start_ts}}
            results = es.search(index=index_name, body=query)

            return results['hits']['hits'][0]['_source'][ts_name]

        def read_ts_test(es, index_name, ts_name, value_name, start_ts, sample_interval, agg_method, buckets_count):

            approx_end_ts = estimate_end_ts(
                start_ts, sample_interval, buckets_count)
            query = {
                "query": {"range": {ts_name: {"gte": start_ts, "lt": approx_end_ts}}},
                "size": 0,  # we aren't interested in records themselves
                "aggs": {
                    "by_sample": {
                        "date_histogram": {
                            "field": ts_name,
                            "interval": sample_interval,
                            "format": esdateformat,
                        },
                        "aggs": {
                            "resampled": {
                                agg_method: {
                                    "field": value_name
                                }
                            }
                        }
                    }
                }
            }

            vs = []
            ts = []

            results = es.search(index=index_name, body=query)

            vs = [x['resampled']['value']  # [value_name]
                  for x in [x for x in results['aggregations']['by_sample']['buckets']]]
            ts = [x['key_as_string']
                  for x in [x for x in results['aggregations']['by_sample']['buckets']]]

            return (vs, ts)

        def read_ts_resampled2(es, index_name, ts_name, value_name, start_ts='',    aggregation=False, sample_interval='1M', agg_method='avg'):
            buckets = 100  # approximate count of buckets to get in one request
            first_ts = get_first_ts(es, index_name, ts_name, start_ts)

            vs = []
            ts = []

            while True:
                nvs, nts = read_ts_test(es, index_name, ts_name, value_name,
                                        first_ts, sample_interval, agg_method, buckets)
                if (len(nts) > 1):
                    # we overlap the last bucket with a new one to fix alignment issues
                    first_ts = nts[-1]
                    nvs.pop()
                    nts.pop()

                    vs.extend(nvs)
                    ts.extend(nts)
                else:
                    vs.extend(nvs)
                    ts.extend(nts)
                    break

            linear_interp(vs)

            return (ts, vs)

        ts, ds = read_ts_resampled2(ivis.elasticsearch,
                                    self.index_name,
                                    self.ts_field,
                                    self.value_field,
                                    self.latest_ts,
                                    aggregation=True,
                                    sample_interval=self.agg_interval,
                                    agg_method=self.agg_method)
        if len(ts) > 0:
            self.set_latest(ts[-1])

        return ds, ts

    def _old_read(self):  # read new observations
        agg = dsl.A('date_histogram', field=self.ts_field,
                    interval=self.agg_interval,
                    format="yyyy-MM-dd'T'HH:mm:ss.SSS'Z'")
        s = dsl.Search(using=ivis.elasticsearch, index=self.index_name).sort(
            {self.ts_field: 'asc'})
        if self.latest_ts:  # query only not yet seen values
            s = s.filter('range', **{self.ts_field: {'gt': self.latest_ts}})
        s.aggs.bucket()

        res = s.execute()
        return res


class PredWriter:
    def __init__(self):
        pass


class PredReader:
    def __init__(self, index_name):
        self.TsReader = TsReader(index_name, 'ts', 'value')

if __name__ == "__main__":
    def test():
        tsr = TsReader('mhn-co2', 'ts', 'value')
        print(tsr._read())

        tsar = TsAggReader('mhn-co2', 'ts', 'value', '1M')
        print(tsar.read())

    test()
