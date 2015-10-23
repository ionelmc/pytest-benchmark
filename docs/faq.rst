Frequently Asked Questions
==========================

Why is my ``StdDev`` so high?
    There can be few causes for this:

    * Bad isolation. You run other services in your machine that eat up your cpu or you run in a VM and that makes
      machine performance inconsistent. Ideally you'd avoid such setups, stop all services and applications and use bare
      metal machines.

    * Bad tests or too much complexity. The function you're testing is doing I/O, using external resources, has
      side-effects or doing other non-deterministic things. Ideally you'd avoid testing huge chunks of code.

      One special situation is PyPy: it's GC and JIT can add unpredictable overhead - you'll see it as huge spikes all
      over the place. You should make sure that you have a good amount of warmup (using ``--benchmark-warmup`` and
      ``--benchmark-warmup-iterations``) to prime the JIT as much as possible. Unfortunately not much can be done about
      GC overhead.

      If you cannot make your tests more predictable and remove overhead you should look at different stats like: IQR and
      Median. IQR is often `better than StdDev
      <https://www.dataz.io/display/Public/2013/03/20/Describing+Data%3A+Why+median+and+IQR+are+often+better+than+mean+and+standard+deviation>`_.

My is my ``Min`` way lower than ``Q1-1.5IQR``?
    You may see this issue in the histogram plot. This is another instance of *bad isolation*.

    For example, Intel CPUs has a feature called `Turbo Boost <https://en.wikipedia.org/wiki/Intel_Turbo_Boost>`_ wich
    overclocks your CPU depending how many cores you have at that time and hot your CPU is. If your CPU is too hot you get
    no Turbo Boost. If you get Turbo Boost active then the CPU quickly gets hot. You can see how this won't work for sustained
    workloads.

    When Turbo Boost kicks in you may see "speed spikes" - and you'd get this strange outlier ``Min``.

    When you have other programs running on your machine you may also see the "speed spikes" - the other programs idle for a
    brief moment and that allows your function to run way faster in that brief moment.

I can't avoid using VMs or running other programs. What can I do?
    As a last ditch effort pytest-benchmark allows you to plugin in custom timers (``--benchmark-timer``). You could use
    something like ``time.process_time`` (Python 3.3+ only) as the timer. Process time `doesn't include sleeping or waiting
    for I/O <https://en.wikipedia.org/wiki/CPU_time>`_.

The histogram doesn't show ``Max`` time. What gives?!
    The height of the plot is limited to ``Q3+1.5IQR`` because ``Max`` has the nasty tendency to be way higher and making
    everything else small and undiscerning. For this reason ``Max`` is *plotted outside*.

    Most people don't care about ``Max`` at all so this is fine.
