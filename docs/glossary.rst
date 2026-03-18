Glossary
========

Iteration
    A single run of your benchmarked function.
Round
    A set of iterations. The size of a `round` is computed in the calibration phase.

    Stats are computed with rounds, not with iterations. The duration for a round is an average of all the iterations in that round.

    See: :doc:`calibration` for an explanation of why it's like this.
Mean
    The arithmetic mean (average) of all round durations.
Median
    The middle value when all round durations are sorted. Unlike the mean, the median is not affected by extreme outliers.
IQR
    Interquartile Range. The difference between the third quartile (Q3) and the first quartile (Q1) of round durations.
    This is a robust way to measure variance that is not affected by outliers.
StdDev
    Standard Deviation. A measure of how spread out the round durations are from the mean.
    A low standard deviation indicates that durations are clustered close to the mean; a high standard deviation indicates more variation.
Outliers
    Rounds with durations that fall significantly outside the typical range.
    Reported as two semicolon-separated counts: StdDev outliers (rounds beyond mean ± 1 standard deviation)
    and IQR outliers (rounds beyond Q1 − 1.5×IQR or Q3 + 1.5×IQR, using Tukey's fences).
