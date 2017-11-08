from pytest import mark

from pytest_benchmark.stats import Stats


def test_1():
    stats = Stats()
    for i in 4., 36., 45., 50., 75.:
        stats.update(i)
    assert stats.mean == 42.
    assert stats.min == 4.
    assert stats.max == 75.
    assert stats.stddev == 25.700194551792794
    assert stats.rounds == 5
    assert stats.total == 210.
    assert stats.ops == 0.023809523809523808


def test_2():
    stats = Stats()
    stats.update(17.)
    stats.update(19.)
    stats.update(24.)
    assert stats.mean == 20.
    assert stats.min == 17.
    assert stats.max == 24.
    assert stats.stddev == 3.605551275463989
    assert stats.rounds == 3
    assert stats.total == 60.
    assert stats.ops == 0.05


def test_single_item():
    stats = Stats()
    stats.update(1)
    assert stats.mean == 1
    assert stats.median == 1
    assert stats.iqr_outliers == 0
    assert stats.stddev_outliers == 0
    assert stats.min == 1
    assert stats.max == 1
    assert stats.stddev == 0
    assert stats.iqr == 0
    assert stats.rounds == 1
    assert stats.total == 1
    assert stats.ld15iqr == 1
    assert stats.hd15iqr == 1
    assert stats.ops == 1


@mark.parametrize('length', range(1, 10))
def test_length(length):
    stats = Stats()
    for i in range(length):
        stats.update(1)

    assert stats.as_dict()


def test_iqr():
    stats = Stats()
    for i in 6, 7, 15, 36, 39, 40, 41, 42, 43, 47, 49:
        stats.update(i)
    assert stats.iqr == 22.5  # https://en.wikipedia.org/wiki/Quartile#Example_1

    stats = Stats()
    for i in 7, 15, 36, 39, 40, 41:
        stats.update(i)
    assert stats.iqr == 25.0  # https://en.wikipedia.org/wiki/Quartile#Example_2

    stats = Stats()
    for i in 1, 2, 3, 4, 5, 6, 7, 8, 9:
        stats.update(i)
    assert stats.iqr == 4.5  # http://www.phusewiki.org/docs/2012/PRESENTATIONS/SP/SP06%20.pdf - method 1

    stats = Stats()
    for i in 1, 2, 3, 4, 5, 6, 7, 8:
        stats.update(i)
    assert stats.iqr == 4.0  # http://www.lexjansen.com/nesug/nesug07/po/po08.pdf - method 1

    stats = Stats()
    for i in 1, 2, 1, 123, 4, 1234, 1, 234, 12, 34, 12, 3, 2, 34, 23:
        stats.update(i)
    assert stats.iqr == 32.0

    stats = Stats()
    for i in 1, 2, 3, 10, 10.1234, 11, 12, 13., 10.1115, 11.1115, 12.1115, 13.5, 10.75, 11.75, 13.12175, 13.1175, 20, \
             50, 52:
        stats.update(i)
    assert stats.stddev == 13.518730097622106
    assert stats.iqr == 3.006212500000002  # close enough: http://www.wessa.net/rwasp_variability.wasp

    stats = Stats()
    for i in [
        11.2, 11.8, 13.2, 12.9, 12.1, 13.5, 14.8, 14.8, 13.6, 11.9, 10.4, 11.8, 11.5, 12.6, 14.1, 13.5, 12.5, 14.9,
        17.0, 17.0, 15.8, 13.3, 11.4, 14.0, 14.5, 15.0, 17.8, 16.3, 17.2, 17.8, 19.9, 19.9, 18.4, 16.2, 14.6, 16.6,
        17.1, 18.0, 19.3, 18.1, 18.3, 21.8, 23.0, 24.2, 20.9, 19.1, 17.2, 19.4, 19.6, 19.6, 23.6, 23.5, 22.9, 24.3,
        26.4, 27.2, 23.7, 21.1, 18.0, 20.1, 20.4, 18.8, 23.5, 22.7, 23.4, 26.4, 30.2, 29.3, 25.9, 22.9, 20.3, 22.9,
        24.2, 23.3, 26.7, 26.9, 27.0, 31.5, 36.4, 34.7, 31.2, 27.4, 23.7, 27.8, 28.4, 27.7, 31.7, 31.3, 31.8, 37.4,
        41.3, 40.5, 35.5, 30.6, 27.1, 30.6, 31.5, 30.1, 35.6, 34.8, 35.5, 42.2, 46.5, 46.7, 40.4, 34.7, 30.5, 33.6,
        34.0, 31.8, 36.2, 34.8, 36.3, 43.5, 49.1, 50.5, 40.4, 35.9, 31.0, 33.7, 36.0, 34.2, 40.6, 39.6, 42.0, 47.2,
        54.8, 55.9, 46.3, 40.7, 36.2, 40.5, 41.7, 39.1, 41.9, 46.1, 47.2, 53.5, 62.2, 60.6, 50.8, 46.1, 39.0, 43.2,
    ]:
        stats.update(i)
    assert stats.iqr == 18.1  # close enough: http://www.wessa.net/rwasp_variability.wasp


def test_ops():
    stats = Stats()
    stats.update(0)
    assert stats.mean == 0
    assert stats.ops == 0


def test_percentile():
    stats = Stats()

    # Taken from http://onlinestatbook.com/2/introduction/percentiles.html
    for i in [4, 4, 5, 5, 5, 5, 6, 6, 6, 7, 7, 7, 8, 8, 9, 9, 9, 10, 10, 10]:
        stats.update(i)

    assert stats.percentile(0.0) == stats.min
    assert stats.percentile(1.0) == stats.max
    assert stats.percentile(0.5) == stats.median
    assert stats.percentile(0.25) == 5.0
    assert stats.percentile(0.85) == 9.849999999999998 # approx(9.85)

    assert hasattr(stats, '_percentile_cache')
    assert 0.85 in stats._percentile_cache
    assert stats._percentile_cache[0.85] == 9.849999999999998 # approx(9.85)


def test_percentile2():
    stats = Stats()

    # Taken from http://www.itl.nist.gov/div898/handbook/prc/section2/prc262.htm
    for i in [95.1772, 95.1567, 95.1937, 95.1959, 95.1442, 95.0610, 95.1591, 95.1195, 95.1065, 95.0925, 95.1990, 95.1682]:
        stats.update(i)

    assert stats.p0 == stats.min
    assert stats.p100 == stats.max
    assert stats.p50 == stats.median
    assert stats.p90 == 95.19807 # approx(95.1981)


def test_extra_fields():
    # Test that percentiles are included in .as_dict() results
    expected = {
        'p85': 9.849999999999998,
        'p25': 5.0,
        "min": 4,
        "max": 10,
        "mean": 7,
        "stddev": 2.0261449005179113,
        "rounds": 20,
        "median": 7.0,
        "iqr": 4.0,
        "q1": 5.0,
        "q3": 9.0,
        "iqr_outliers": 0,
        "stddev_outliers": 5,
        "outliers": '5;0',
        "ld15iqr": 4,
        "hd15iqr": 10,
        "ops": 0.14285714285714285,
        "total": 140,
    }

    stats = Stats()

    for i in [4, 4, 5, 5, 5, 5, 6, 6, 6, 7, 7, 7, 8, 8, 9, 9, 9, 10, 10, 10]:
        stats.update(i)

    result = stats.as_dict(extra_fields=('p25', 'p85'))

    assert result == expected
