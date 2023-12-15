Glossary
========

Iteration
    A single run of your benchmarked function.
Round
    A set of iterations. The size of a `round` is computed in the calibration phase.

    Stats are computed with rounds, not with iterations. The duration for a round is an average of all the iterations in that round.

    See: :doc:`calibration` for an explanation of why it's like this.
Mean
    Arithmetic mean. Sum of all entries divided by count.
Median
    Value of middle entry, when all entries are sorted in ascending order.
    If number of entries is odd, choise of middle value varies based on context. Here
    middle index is computed as `length // 2`, thus selecting lower value for median.
IQR
    InterQuertile Range. This is a different way to measure variance.
StdDev
    Common measure of spread in statistics. The more wide values are spread, the higher
    standard deviation is.

    Often written as *σ*. Another related metric is *variance*, which is just standard
    deviation squared, *σ^2*
Outliers
    Values which differ significantly from other observations. More precise definition depends
    on context, and could be defined as those outside specific *percentiles* (e.g. p90) or
    are further away from mean than given number of *sigmas* (StdDev)
