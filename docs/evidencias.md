\# Evidências do Projeto Prático - pytest-benchmark



\## Projeto escolhido



Repositório original: https://github.com/ionelmc/pytest-benchmark



O projeto escolhido foi o pytest-benchmark, um plugin para pytest usado para medir desempenho de funções Python e comparar resultados de benchmark.



\## Próximas evidências



\- Execução dos testes com pytest

\- Relatório de cobertura

\- GitHub Actions

\- SonarCloud

\- Novos testes

\- Duas mudanças no sistema

\- Pull request para o projeto original



\## Testes com pytest



Commando executado:



```bash

pytest -o addopts=""



Resultado:

(venv) PS C:\\Users\\Isabela Castro\\Documents\\Faculdade\\ES2\\projetoES2\\pytest-benchmark> pytest -o addopts=""

================================================= test session starts ==================================================

platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0

benchmark: 5.2.3 (defaults: timer=time.perf\_counter disable\_gc=False min\_rounds=5 min\_time=0.000005 max\_time=1.0 calibration\_precision=10 warmup=False warmup\_iterations=100000)

rootdir: C:\\Users\\Isabela Castro\\Documents\\Faculdade\\ES2\\projetoES2\\pytest-benchmark

configfile: pytest.ini

testpaths: tests

plugins: nbmake-1.5.5, benchmark-5.2.3, cov-7.1.0

collected 237 items / 1 skipped



tests\\test\_benchmark.py ..........................................ss.........                                     \[ 22%]

tests\\test\_calibration.py ..................................                                                      \[ 36%]

tests\\test\_cli.py ............F........                                                                           \[ 45%]

tests\\test\_normal.py s...sssss                                                                                    \[ 49%]

tests\\test\_pedantic.py .......................                                                                    \[ 59%]

tests\\test\_sample.py ....                                                                                         \[ 60%]

tests\\test\_skip.py s                                                                                              \[ 61%]

tests\\test\_stats.py ..............                                                                                \[ 67%]

tests\\test\_storage.py ........................................                                                    \[ 83%]

tests\\test\_utils.py .....ss..ss.s......s..s..s..s.....                                                            \[ 98%]

tests\\test\_with\_testcase.py .FE                                                                                   \[ 99%]

tests\\test\_with\_weaver.py FEFE                                                                                    \[100%]



======================================================== ERRORS ========================================================

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ ERROR at teardown of TerribleTerribleWayToWritePatchTests.test\_foo2 \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



request = <SubRequest 'benchmark' for <TestCaseFunction test\_foo2>>



&#x20;   @pytest.fixture

&#x20;   def benchmark(request):

&#x20;       bs: BenchmarkSession = request.config.\_benchmarksession

&#x20;

&#x20;       if bs.skip:

&#x20;           pytest.skip('Benchmarks are skipped (--benchmark-skip was used).')

&#x20;       else:

&#x20;           node = request.node

&#x20;           marker = node.get\_closest\_marker('benchmark')

&#x20;           options: dict\[str, object] = dict(marker.kwargs) if marker else {}

&#x20;           if 'timer' in options:

&#x20;               options\['timer'] = NameWrapper(options\['timer'])

&#x20;           fixture = BenchmarkFixture(

&#x20;               node,

&#x20;               add\_stats=bs.benchmarks.append,

&#x20;               logger=bs.logger,

&#x20;               warner=request.node.warn,

&#x20;               disabled=bs.disabled,

&#x20;               \*\*dict(bs.options, \*\*options),

&#x20;           )

&#x20;           yield fixture

>           fixture.\_cleanup()



src\\pytest\_benchmark\\plugin.py:485:

\_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_

src\\pytest\_benchmark\\fixture.py:353: in \_cleanup

&#x20;   self.\_logger.warning('Benchmark fixture was not used at all in this test!', warner=self.\_warner, suspend=True)

\_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_



self = <pytest\_benchmark.logger.Logger object at 0x00000225F74094D0>

text = 'Benchmark fixture was not used at all in this test!'

warner = <bound method Node.warn of <TestCaseFunction test\_foo2>>, suspend = True



&#x20;   def warning(self, text, warner=None, suspend=False):

&#x20;       if self.level >= self.VERBOSE:

&#x20;           if suspend and self.suspend\_capture:

&#x20;               self.suspend\_capture(in\_=True)

&#x20;           self.term.line('')

&#x20;           self.term.sep('-', red=True, bold=True)

&#x20;           self.term.write(' WARNING: ', red=True, bold=True)

&#x20;           self.term.line(text, red=True)

&#x20;           self.term.sep('-', red=True, bold=True)

&#x20;           if suspend and self.resume\_capture:

&#x20;               self.resume\_capture()

&#x20;       if warner is None:

&#x20;           warner = warnings.warn

>       warner(PytestBenchmarkWarning(text))

E       pytest\_benchmark.logger.PytestBenchmarkWarning: Benchmark fixture was not used at all in this test!



src\\pytest\_benchmark\\logger.py:44: PytestBenchmarkWarning

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ ERROR at teardown of test\_weave\_fixture \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



request = <SubRequest 'benchmark' for <Function test\_weave\_fixture>>



&#x20;   @pytest.fixture

&#x20;   def benchmark(request):

&#x20;       bs: BenchmarkSession = request.config.\_benchmarksession

&#x20;

&#x20;       if bs.skip:

&#x20;           pytest.skip('Benchmarks are skipped (--benchmark-skip was used).')

&#x20;       else:

&#x20;           node = request.node

&#x20;           marker = node.get\_closest\_marker('benchmark')

&#x20;           options: dict\[str, object] = dict(marker.kwargs) if marker else {}

&#x20;           if 'timer' in options:

&#x20;               options\['timer'] = NameWrapper(options\['timer'])

&#x20;           fixture = BenchmarkFixture(

&#x20;               node,

&#x20;               add\_stats=bs.benchmarks.append,

&#x20;               logger=bs.logger,

&#x20;               warner=request.node.warn,

&#x20;               disabled=bs.disabled,

&#x20;               \*\*dict(bs.options, \*\*options),

&#x20;           )

&#x20;           yield fixture

>           fixture.\_cleanup()



src\\pytest\_benchmark\\plugin.py:485:

\_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_

src\\pytest\_benchmark\\fixture.py:353: in \_cleanup

&#x20;   self.\_logger.warning('Benchmark fixture was not used at all in this test!', warner=self.\_warner, suspend=True)

\_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_



self = <pytest\_benchmark.logger.Logger object at 0x00000225F74094D0>

text = 'Benchmark fixture was not used at all in this test!'

warner = <bound method Node.warn of <Function test\_weave\_fixture>>, suspend = True



&#x20;   def warning(self, text, warner=None, suspend=False):

&#x20;       if self.level >= self.VERBOSE:

&#x20;           if suspend and self.suspend\_capture:

&#x20;               self.suspend\_capture(in\_=True)

&#x20;           self.term.line('')

&#x20;           self.term.sep('-', red=True, bold=True)

&#x20;           self.term.write(' WARNING: ', red=True, bold=True)

&#x20;           self.term.line(text, red=True)

&#x20;           self.term.sep('-', red=True, bold=True)

&#x20;           if suspend and self.resume\_capture:

&#x20;               self.resume\_capture()

&#x20;       if warner is None:

&#x20;           warner = warnings.warn

>       warner(PytestBenchmarkWarning(text))

E       pytest\_benchmark.logger.PytestBenchmarkWarning: Benchmark fixture was not used at all in this test!



src\\pytest\_benchmark\\logger.py:44: PytestBenchmarkWarning

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ ERROR at teardown of test\_weave\_method \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



request = <SubRequest 'benchmark' for <Function test\_weave\_method>>



&#x20;   @pytest.fixture

&#x20;   def benchmark(request):

&#x20;       bs: BenchmarkSession = request.config.\_benchmarksession

&#x20;

&#x20;       if bs.skip:

&#x20;           pytest.skip('Benchmarks are skipped (--benchmark-skip was used).')

&#x20;       else:

&#x20;           node = request.node

&#x20;           marker = node.get\_closest\_marker('benchmark')

&#x20;           options: dict\[str, object] = dict(marker.kwargs) if marker else {}

&#x20;           if 'timer' in options:

&#x20;               options\['timer'] = NameWrapper(options\['timer'])

&#x20;           fixture = BenchmarkFixture(

&#x20;               node,

&#x20;               add\_stats=bs.benchmarks.append,

&#x20;               logger=bs.logger,

&#x20;               warner=request.node.warn,

&#x20;               disabled=bs.disabled,

&#x20;               \*\*dict(bs.options, \*\*options),

&#x20;           )

&#x20;           yield fixture

>           fixture.\_cleanup()



src\\pytest\_benchmark\\plugin.py:485:

\_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_

src\\pytest\_benchmark\\fixture.py:353: in \_cleanup

&#x20;   self.\_logger.warning('Benchmark fixture was not used at all in this test!', warner=self.\_warner, suspend=True)

\_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_



self = <pytest\_benchmark.logger.Logger object at 0x00000225F74094D0>

text = 'Benchmark fixture was not used at all in this test!'

warner = <bound method Node.warn of <Function test\_weave\_method>>, suspend = True



&#x20;   def warning(self, text, warner=None, suspend=False):

&#x20;       if self.level >= self.VERBOSE:

&#x20;           if suspend and self.suspend\_capture:

&#x20;               self.suspend\_capture(in\_=True)

&#x20;           self.term.line('')

&#x20;           self.term.sep('-', red=True, bold=True)

&#x20;           self.term.write(' WARNING: ', red=True, bold=True)

&#x20;           self.term.line(text, red=True)

&#x20;           self.term.sep('-', red=True, bold=True)

&#x20;           if suspend and self.resume\_capture:

&#x20;               self.resume\_capture()

&#x20;       if warner is None:

&#x20;           warner = warnings.warn

>       warner(PytestBenchmarkWarning(text))

E       pytest\_benchmark.logger.PytestBenchmarkWarning: Benchmark fixture was not used at all in this test!



src\\pytest\_benchmark\\logger.py:44: PytestBenchmarkWarning

======================================================= FAILURES =======================================================

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ test\_compare\_between \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



testdir = testdir(makepyfile=<bound method Testdir.makepyfile of <Testdir local('C:\\\\Users\\\\Isabela Castro\\\\AppData\\\\Local\\\\Temp...t-of-Isabela Castro\\\\pytest-0\\\\test\_compare\_between0'), run=<function testdir.<locals>.<lambda> at 0x0000022600839940>)



&#x20;   def test\_compare\_between(testdir):

&#x20;       common\_args = \[

&#x20;           'py.test-benchmark',

&#x20;           '--storage',

&#x20;           STORAGE,

&#x20;           'compare',

&#x20;           '--between=min,max',

&#x20;           '--sort=min',

&#x20;           '--name=short',

&#x20;       ]

&#x20;       # 2-source case: per-metric grouping with ref + delta

&#x20;       result = testdir.run(\*common\_args, '0001', '0002')

>       result.stdout.fnmatch\_lines(

&#x20;           \[

&#x20;               '---\*--- benchmark: 1 tests, 2 sources ---\*---',

&#x20;               'Name (time in ns) \*0001 Min\*0002 Min\*\\u0394Min\*0001 Max\*0002 Max\*\\u0394Max',

&#x20;               '---\*---',

&#x20;               'xfast\_parametrized\[\[]0\[]] \*217.3145\*216.9028\*-0.2%\*11\*447.3891\*7\*739.2997\*-32.4%',

&#x20;               '---\*---',

&#x20;           ]

&#x20;       )

E       Failed: nomatch: '---\*--- benchmark: 1 tests, 2 sources ---\*---'

E           and: ''

E       fnmatch: '---\*--- benchmark: 1 tests, 2 sources ---\*---'

E          with: '----------------------------- benchmark: 1 tests, 2 sources -----------------------------'

E       nomatch: 'Name (time in ns) \*0001 Min\*0002 Min\*ΔMin\*0001 Max\*0002 Max\*ΔMax'

E           and: 'Name (time in ns)         0001 Min  0002 Min      \\\\u0394Min     0001 Max    0002 Max      \\\\u0394Max'

E           and: '-----------------------------------------------------------------------------------------'

E           and: 'xfast\_parametrized\[0]     217.3145  216.9028     -0.2%  11,447.3891  7,739.2997    -32.4%'

E           and: '-----------------------------------------------------------------------------------------'

E           and: ''

E           and: 'Legend:'

E           and: '  Cyan: reference source for comparison. Green: improvement, Red: regression.'

E           and: '  \\\\u0394: percentage change from reference source.'

E       remains unmatched: 'Name (time in ns) \*0001 Min\*0002 Min\*ΔMin\*0001 Max\*0002 Max\*ΔMax'



C:\\Users\\Isabela Castro\\Documents\\Faculdade\\ES2\\projetoES2\\pytest-benchmark\\tests\\test\_cli.py:309: Failed

\------------------------------------------------- Captured stdout call -------------------------------------------------

running: py.test-benchmark.exe --storage C:\\Users\\Isabela Castro\\Documents\\Faculdade\\ES2\\projetoES2\\pytest-benchmark\\tests\\test\_storage compare --between=min,max --sort=min --name=short 0001 0002

&#x20;    in: C:\\Users\\Isabela Castro\\AppData\\Local\\Temp\\pytest-of-Isabela Castro\\pytest-0\\test\_compare\_between0



\----------------------------- benchmark: 1 tests, 2 sources -----------------------------

Name (time in ns)         0001 Min  0002 Min      \\u0394Min     0001 Max    0002 Max      \\u0394Max

\-----------------------------------------------------------------------------------------

xfast\_parametrized\[0]     217.3145  216.9028     -0.2%  11,447.3891  7,739.2997    -32.4%

\-----------------------------------------------------------------------------------------



Legend:

&#x20; Cyan: reference source for comparison. Green: improvement, Red: regression.

&#x20; \\u0394: percentage change from reference source.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ TerribleTerribleWayToWritePatchTests.test\_foo2 \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



name = 'aspectlib', path = None, target = None



>   ???

E   AttributeError: 'PluginImportFixer' object has no attribute 'find\_spec'



<frozen importlib.\_bootstrap>:1072: AttributeError



During handling of the above exception, another exception occurred:



self = <test\_with\_testcase.TerribleTerribleWayToWritePatchTests testMethod=test\_foo2>



&#x20;   def test\_foo2(self):

>       self.benchmark\_weave('time.sleep')



tests\\test\_with\_testcase.py:22:

\_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_

src\\pytest\_benchmark\\fixture.py:334: in weave

&#x20;   import aspectlib  # noqa: PLC0415

&#x20;   ^^^^^^^^^^^^^^^^

<frozen importlib.\_bootstrap>:1176: in \_find\_and\_load

&#x20;   ???

<frozen importlib.\_bootstrap>:1138: in \_find\_and\_load\_unlocked

&#x20;   ???

<frozen importlib.\_bootstrap>:1074: in \_find\_spec

&#x20;   ???

\_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_



finder = <pygal.PluginImportFixer object at 0x00000226018F2350>, name = 'aspectlib', path = None



>   ???

E   ImportWarning: PluginImportFixer.find\_spec() not found; falling back to find\_module()



<frozen importlib.\_bootstrap>:1047: ImportWarning

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ test\_weave\_fixture \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



name = 'aspectlib', path = None, target = None



>   ???

E   AttributeError: 'PluginImportFixer' object has no attribute 'find\_spec'



<frozen importlib.\_bootstrap>:1072: AttributeError



During handling of the above exception, another exception occurred:



benchmark\_weave = <bound method BenchmarkFixture.weave of <pytest\_benchmark.fixture.BenchmarkFixture object at 0x00000225F74D9510>>



&#x20;   @pytest.mark.benchmark(max\_time=0.001)

&#x20;   def test\_weave\_fixture(benchmark\_weave):

>       benchmark\_weave(Foo.internal, lazy=True)



tests\\test\_with\_weaver.py:19:

\_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_

src\\pytest\_benchmark\\fixture.py:334: in weave

&#x20;   import aspectlib  # noqa: PLC0415

&#x20;   ^^^^^^^^^^^^^^^^

<frozen importlib.\_bootstrap>:1176: in \_find\_and\_load

&#x20;   ???

<frozen importlib.\_bootstrap>:1138: in \_find\_and\_load\_unlocked

&#x20;   ???

<frozen importlib.\_bootstrap>:1074: in \_find\_spec

&#x20;   ???

\_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_



finder = <pygal.PluginImportFixer object at 0x00000226018F2350>, name = 'aspectlib', path = None



>   ???

E   ImportWarning: PluginImportFixer.find\_spec() not found; falling back to find\_module()



<frozen importlib.\_bootstrap>:1047: ImportWarning

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ test\_weave\_method \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



name = 'aspectlib', path = None, target = None



>   ???

E   AttributeError: 'PluginImportFixer' object has no attribute 'find\_spec'



<frozen importlib.\_bootstrap>:1072: AttributeError



During handling of the above exception, another exception occurred:



benchmark = <pytest\_benchmark.fixture.BenchmarkFixture object at 0x00000225F7458250>



&#x20;   @pytest.mark.benchmark(max\_time=0.001)

&#x20;   def test\_weave\_method(benchmark):

>       benchmark.weave(Foo.internal, lazy=True)



tests\\test\_with\_weaver.py:26:

\_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_

src\\pytest\_benchmark\\fixture.py:334: in weave

&#x20;   import aspectlib  # noqa: PLC0415

&#x20;   ^^^^^^^^^^^^^^^^

<frozen importlib.\_bootstrap>:1176: in \_find\_and\_load

&#x20;   ???

<frozen importlib.\_bootstrap>:1138: in \_find\_and\_load\_unlocked

&#x20;   ???

<frozen importlib.\_bootstrap>:1074: in \_find\_spec

&#x20;   ???

\_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_



finder = <pygal.PluginImportFixer object at 0x00000226018F2350>, name = 'aspectlib', path = None



>   ???

E   ImportWarning: PluginImportFixer.find\_spec() not found; falling back to find\_module()



<frozen importlib.\_bootstrap>:1047: ImportWarning



\------------------------------------------------------------------------------------------------------------------------------------ benchmark: 56 tests -------------------------------------------------------------------------------------------------------------------------------------

Name (time in ns)                                                     Min                             Max                            Mean                  StdDev                          Median                     IQR            Outliers               OPS             Rounds  Iterations

\----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

test\_rounds                                                        0.0000 (1.0)                  300.0023 (59.41)                100.0008 (19.80)         65.4659 (inf)                  100.0008 (19.80)          0.0000 (1.0)           3;3    9,999,923.8556 (0.05)          15           1

test\_warmup\_rounds                                                 0.0000 (1.0)                  100.0008 (19.80)                 80.0006 (15.84)         44.7217 (inf)                  100.0008 (19.80)         25.0002 (inf)           1;1   12,499,904.8196 (0.06)           5           1

test\_calibrate\_stuck\[False--1-1e-10]                               5.0500 (inf)                    5.0500 (1.0)                    5.0500 (1.0)            0.0000 (1.0)                    5.0500 (1.0)            0.0000 (1.0)           0;0  198,019,801.9802 (1.0)            1           2

test\_calibrate\_stuck\[False-0-1e-10]                                5.0500 (inf)                    5.0500 (1.00)                   5.0500 (1.00)           0.0000 (1.0)                    5.0500 (1.00)           0.0000 (1.0)           0;0  198,019,801.9802 (1.00)           1           2

test\_calibrate\_stuck\[False-1-1e-10]                                5.0500 (inf)                    5.0500 (1.00)                   5.0500 (1.00)           0.0000 (1.0)                    5.0500 (1.00)           0.0000 (1.0)           0;0  198,019,801.9802 (1.00)           1           2

test\_calibrate\_stuck\[True--1-1e-10]                               10.0000 (inf)                   10.0000 (1.98)                  10.0000 (1.98)           0.0000 (1.0)                   10.0000 (1.98)           0.0000 (1.0)           0;0  100,000,000.0000 (0.51)           1           1

test\_calibrate\_stuck\[True-0-1e-10]                                10.0000 (inf)                   10.0000 (1.98)                  10.0000 (1.98)           0.0000 (1.0)                   10.0000 (1.98)           0.0000 (1.0)           0;0  100,000,000.0000 (0.50)           1           1

test\_calibrate\_stuck\[True-1-1e-10]                                10.0000 (inf)                   10.0000 (1.98)                  10.0000 (1.98)           0.0000 (1.0)                   10.0000 (1.98)           0.0000 (1.0)           0;0  100,000,000.0000 (0.50)           1           1

test\_calibrate\_xfast                                              34.4593 (inf)              102,971.6219 (>1000.0)              128.1931 (25.38)        135.5518 (inf)                  139.8647 (27.70)         68.2434 (inf)    20979;25445    7,800,732.6121 (0.04)     1851858         148

test\_xfast                                                        38.3251 (inf)                   43.5276 (8.62)                  40.9263 (8.10)           3.6787 (inf)                   40.9263 (8.10)           5.2025 (inf)           0;0   24,434,143.5708 (0.12)           2     1000000

test\_rounds\_iterations                                            50.0004 (inf)                1,149.9971 (227.72)               153.3333 (30.36)        277.0156 (inf)                   80.0006 (15.84)         50.0004 (inf)           1;1    6,521,738.9857 (0.03)          15          10

test\_calibrate\_stuck\[False--1-1e-09]                              50.5000 (inf)                   50.5000 (10.00)                 50.5000 (10.00)          0.0000 (1.0)                   50.5000 (10.00)          0.0000 (1.0)           0;0   19,801,980.1980 (0.10)           1           2

test\_calibrate\_stuck\[False-0-1e-09]                               50.5000 (inf)                   50.5000 (10.00)                 50.5000 (10.00)          0.0000 (1.0)                   50.5000 (10.00)          0.0000 (1.0)           0;0   19,801,980.1980 (0.10)           1           2

test\_calibrate\_stuck\[False-1-1e-09]                               50.5000 (inf)                   50.5000 (10.00)                 50.5000 (10.00)          0.0000 (1.0)                   50.5000 (10.00)          0.0000 (1.0)           0;0   19,801,980.1980 (0.10)           1           2

test\_proto\[CachedPropertyProxy]                                   68.8881 (inf)               18,128.8885 (>1000.0)               97.9299 (19.39)         87.9416 (inf)                   95.5563 (18.92)         15.5570 (inf)     1595;4479   10,211,387.8457 (0.05)      196080          45

test\_proto\[LocalsCachedPropertyProxy]                             72.3397 (inf)               28,959.5745 (>1000.0)              104.4828 (20.69)        111.4856 (inf)                  104.2561 (20.64)         14.8937 (inf)      667;5089    9,570,956.3049 (0.05)      199999          47

test\_proto\[LocalsSimpleProxy]                                     72.4998 (inf)                8,481.2498 (>1000.0)              105.6258 (20.92)         75.1823 (inf)                  104.3747 (20.67)         16.2501 (inf)      645;1752    9,467,384.7078 (0.05)       47394         160

test\_proto\[SimpleProxy]                                           74.9977 (inf)               17,809.9988 (>1000.0)              110.3563 (21.85)        125.1401 (inf)                  109.9979 (21.78)         15.0001 (inf)      249;2032    9,061,556.4038 (0.05)       76336          20

test\_calibrate\_stuck\[True--1-1e-09]                              100.0000 (inf)                  100.0000 (19.80)                100.0000 (19.80)          0.0000 (1.0)                  100.0000 (19.80)          0.0000 (1.0)           0;0   10,000,000.0000 (0.05)           1           1

test\_calibrate\_stuck\[True-0-1e-09]                               100.0000 (inf)                  100.0000 (19.80)                100.0000 (19.80)          0.0000 (1.0)                  100.0000 (19.80)          0.0000 (1.0)           0;0   10,000,000.0000 (0.05)           1           1

test\_calibrate\_stuck\[True-1-1e-09]                               100.0000 (inf)                  100.0000 (19.80)                100.0000 (19.80)          0.0000 (1.0)                  100.0000 (19.80)          0.0000 (1.0)           0;0   10,000,000.0000 (0.05)           1           1

test\_iterations                                                  100.0008 (inf)                  100.0008 (19.80)                100.0008 (19.80)          0.0000 (1.0)                  100.0008 (19.80)          0.0000 (1.0)           0;0    9,999,923.8556 (0.05)           1          10

test\_teardown\_many\_rounds                                        100.0008 (inf)                1,400.0107 (277.23)               489.9979 (97.03)        395.6739 (inf)                  350.0027 (69.31)        400.0030 (inf)           2;1    2,040,825.0299 (0.01)          10           1

test\_calibrate\_fast                                              149.0000 (inf)               74,954.9997 (>1000.0)              719.0529 (142.39)       369.9496 (inf)                  807.0003 (159.80)       434.9998 (inf)    17869;8396    1,390,718.2823 (0.01)      657895         100

test\_setup\_many\_rounds                                           200.0015 (inf)                1,000.0076 (198.02)               410.0031 (81.19)        268.5372 (inf)                  300.0023 (59.41)        400.0030 (inf)           2;0    2,439,005.8185 (0.01)          10           1

test\_single                                                      300.0023 (inf)                  300.0023 (59.41)                300.0023 (59.41)          0.0000 (1.0)                  300.0023 (59.41)          0.0000 (1.0)           0;0    3,333,307.9519 (0.02)           1           1

test\_teardown\_many\_iterations                                    300.0023 (inf)                  300.0023 (59.41)                300.0023 (59.41)          0.0000 (1.0)                  300.0023 (59.41)          0.0000 (1.0)           0;0    3,333,307.9519 (0.02)           1           3

test\_can\_use\_both\_args\_and\_setup\_without\_return                  600.0046 (inf)                  600.0046 (118.81)               600.0046 (118.81)         0.0000 (1.0)                  600.0046 (118.81)         0.0000 (1.0)           0;0    1,666,653.9759 (0.01)           1           1

test\_teardown                                                    600.0046 (inf)                  600.0046 (118.81)               600.0046 (118.81)         0.0000 (1.0)                  600.0046 (118.81)         0.0000 (1.0)           0;0    1,666,653.9759 (0.01)           1           1

test\_teardown\_cprofile                                           600.0046 (inf)                  600.0046 (118.81)               600.0046 (118.81)         0.0000 (1.0)                  600.0046 (118.81)         0.0000 (1.0)           0;0    1,666,653.9759 (0.01)           1           1

test\_args\_kwargs                                                 700.0053 (inf)                  700.0053 (138.61)               700.0053 (138.61)         0.0000 (1.0)                  700.0053 (138.61)         0.0000 (1.0)           0;0    1,428,560.5508 (0.01)           1           1

test\_setup                                                       700.0053 (inf)                  700.0053 (138.61)               700.0053 (138.61)         0.0000 (1.0)                  700.0053 (138.61)         0.0000 (1.0)           0;0    1,428,560.5508 (0.01)           1           1

test\_setup\_cprofile                                            1,399.9525 (inf)                1,399.9525 (277.22)             1,399.9525 (277.22)         0.0000 (1.0)                1,399.9525 (277.22)         0.0000 (1.0)           0;0      714,309.9740 (0.00)           1           1

test\_calibrate                                                12,699.9803 (inf)            5,852,999.9806 (>1000.0)           17,494.9990 (>1000.0)   16,800.8265 (inf)               17,399.9579 (>1000.0)    3,599.9692 (inf)    8036;23926       57,159.1917 (0.00)      833332           1

test\_foo                                                      14,299.9925 (inf)            6,345,999.9510 (>1000.0)          618,437.4918 (>1000.0)  176,414.7153 (inf)              570,099.9754 (>1000.0)  156,125.0683 (inf)     2101;1302        1,616.9783 (0.00)       17065           1

test\_calibrate\_slow                                           24,600.0127 (inf)           10,344,100.0101 (>1000.0)          617,035.9334 (>1000.0)  160,855.6844 (inf)              569,799.9732 (>1000.0)  107,700.0052 (inf)    39145;30021        1,620.6512 (0.00)      355872           1

test\_slow                                                  1,040,300.0051 (inf)            5,759,400.0245 (>1000.0)        1,655,816.1385 (>1000.0)  278,187.0419 (inf)            1,682,400.0049 (>1000.0)  273,349.9859 (inf)        163;20          603.9318 (0.00)         849           1

test\_slower                                               10,099,500.0103 (inf)           12,837,899.9652 (>1000.0)       10,558,274.1928 (>1000.0)  405,681.2626 (inf)           10,495,299.9973 (>1000.0)  298,324.9869 (inf)           9;4           94.7124 (0.00)          93           1

test\_calibrate\_stuck\[False--1-0.01]                      505,000,000.0000 (inf)          505,000,000.0000 (>1000.0)      505,000,000.0000 (>1000.0)        0.0000 (1.0)          505,000,000.0000 (>1000.0)        0.0000 (1.0)           0;0            1.9802 (0.00)           1           2

test\_calibrate\_stuck\[False-0-0.01]                       505,000,000.0000 (inf)          505,000,000.0000 (>1000.0)      505,000,000.0000 (>1000.0)        0.0000 (1.0)          505,000,000.0000 (>1000.0)        0.0000 (1.0)           0;0            1.9802 (0.00)           1           2

test\_calibrate\_stuck\[False-1-0.01]                       505,000,000.0000 (inf)          505,000,000.0000 (>1000.0)      505,000,000.0000 (>1000.0)        0.0000 (1.0)          505,000,000.0000 (>1000.0)        0.0000 (1.0)           0;0            1.9802 (0.00)           1           2

test\_calibrate\_stuck\[True--1-0.01]                     1,000,000,000.0000 (inf)        1,000,000,000.0000 (>1000.0)    1,000,000,000.0000 (>1000.0)        0.0000 (1.0)        1,000,000,000.0000 (>1000.0)        0.0000 (1.0)           0;0            1.0000 (0.00)           1           1

test\_calibrate\_stuck\[True-0-0.01]                      1,000,000,000.0000 (inf)        1,000,000,000.0000 (>1000.0)    1,000,000,000.0000 (>1000.0)        0.0000 (1.0)        1,000,000,000.0000 (>1000.0)        0.0000 (1.0)           0;0            1.0000 (0.00)           1           1

test\_calibrate\_stuck\[True-1-0.01]                      1,000,000,000.0000 (inf)        1,000,000,000.0000 (>1000.0)    1,000,000,000.0000 (>1000.0)        0.0000 (1.0)        1,000,000,000.0000 (>1000.0)        0.0000 (1.0)           0;0            1.0000 (0.00)           1           1

test\_calibrate\_stuck\[False--1-1.000000000000001]      50,500,000,000.0000 (inf)       50,500,000,000.0000 (>1000.0)   50,500,000,000.0000 (>1000.0)        0.0000 (1.0)       50,500,000,000.0000 (>1000.0)        0.0000 (1.0)           0;0            0.0198 (0.00)           1           2

test\_calibrate\_stuck\[False--1-1]                      50,500,000,000.0000 (inf)       50,500,000,000.0000 (>1000.0)   50,500,000,000.0000 (>1000.0)        0.0000 (1.0)       50,500,000,000.0000 (>1000.0)        0.0000 (1.0)           0;0            0.0198 (0.00)           1           2

test\_calibrate\_stuck\[False-0-1]                       50,500,000,000.0000 (inf)       50,500,000,000.0000 (>1000.0)   50,500,000,000.0000 (>1000.0)        0.0000 (1.0)       50,500,000,000.0000 (>1000.0)        0.0000 (1.0)           0;0            0.0198 (0.00)           1           2

test\_calibrate\_stuck\[False-1-1]                       50,500,000,000.0000 (inf)       50,500,000,000.0000 (>1000.0)   50,500,000,000.0000 (>1000.0)        0.0000 (1.0)       50,500,000,000.0000 (>1000.0)        0.0000 (1.0)           0;0            0.0198 (0.00)           1           2

test\_calibrate\_stuck\[False-0-1.000000000000001]       50,500,000,000.0001 (inf)       50,500,000,000.0001 (>1000.0)   50,500,000,000.0001 (>1000.0)        0.0000 (1.0)       50,500,000,000.0001 (>1000.0)        0.0000 (1.0)           0;0            0.0198 (0.00)           1           2

test\_calibrate\_stuck\[False-1-1.000000000000001]       50,500,000,000.0001 (inf)       50,500,000,000.0001 (>1000.0)   50,500,000,000.0001 (>1000.0)        0.0000 (1.0)       50,500,000,000.0001 (>1000.0)        0.0000 (1.0)           0;0            0.0198 (0.00)           1           2

test\_calibrate\_stuck\[True--1-1]                       75,000,000,000.0000 (inf)       75,000,000,000.0000 (>1000.0)   75,000,000,000.0000 (>1000.0)        0.0000 (1.0)       75,000,000,000.0000 (>1000.0)        0.0000 (1.0)           0;0            0.0133 (0.00)           1           2

test\_calibrate\_stuck\[True--1-1.000000000000001]       99,999,999,999.9999 (inf)       99,999,999,999.9999 (>1000.0)   99,999,999,999.9999 (>1000.0)        0.0000 (1.0)       99,999,999,999.9999 (>1000.0)        0.0000 (1.0)           0;0            0.0100 (0.00)           1           1

test\_calibrate\_stuck\[True-0-1]                       100,000,000,000.0000 (inf)      100,000,000,000.0000 (>1000.0)  100,000,000,000.0000 (>1000.0)        0.0000 (1.0)      100,000,000,000.0000 (>1000.0)        0.0000 (1.0)           0;0            0.0100 (0.00)           1           1

test\_calibrate\_stuck\[True-1-1]                       100,000,000,000.0001 (inf)      100,000,000,000.0001 (>1000.0)  100,000,000,000.0001 (>1000.0)        0.0000 (1.0)      100,000,000,000.0001 (>1000.0)        0.0000 (1.0)           0;0            0.0100 (0.00)           1           1

test\_calibrate\_stuck\[True-0-1.000000000000001]       100,000,000,000.0001 (inf)      100,000,000,000.0001 (>1000.0)  100,000,000,000.0001 (>1000.0)        0.0000 (1.0)      100,000,000,000.0001 (>1000.0)        0.0000 (1.0)           0;0            0.0100 (0.00)           1           1

test\_calibrate\_stuck\[True-1-1.000000000000001]       100,000,000,000.0003 (inf)      100,000,000,000.0003 (>1000.0)  100,000,000,000.0003 (>1000.0)        0.0000 (1.0)      100,000,000,000.0003 (>1000.0)        0.0000 (1.0)           0;0            0.0100 (0.00)           1           1

\----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



Legend:

&#x20; Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd Quartile.

&#x20; OPS: Operations Per Second, computed as 1 / Mean

\------------------------------------------------- cProfile (time in s) -------------------------------------------------

tests/test\_pedantic.py::test\_setup\_cprofile

ncalls  tottime percall cumtime percall filename:lineno(function)

1       0.0000  0.0000  0.0000  0.0000  \\pytest-benchmark\\tests\\test\_pedantic.py:42(stuff)

1       0.0000  0.0000  0.0000  0.0000  \~:0(<method 'append' of 'list' objects>)

1       0.0000  0.0000  0.0000  0.0000  \~:0(<method 'disable' of '\_lsprof.Profiler' objects>)



tests/test\_pedantic.py::test\_teardown\_cprofile

ncalls  tottime percall cumtime percall filename:lineno(function)

1       0.0000  0.0000  0.0000  0.0000  \\pytest-benchmark\\tests\\test\_pedantic.py:56(stuff)

1       0.0000  0.0000  0.0000  0.0000  \~:0(<method 'append' of 'list' objects>)

1       0.0000  0.0000  0.0000  0.0000  \~:0(<method 'disable' of '\_lsprof.Profiler' objects>)



=============================================== short test summary info ================================================

FAILED tests/test\_cli.py::test\_compare\_between - Failed: nomatch: '---\*--- benchmark: 1 tests, 2 sources ---\*---'

FAILED tests/test\_with\_testcase.py::TerribleTerribleWayToWritePatchTests::test\_foo2 - ImportWarning: PluginImportFixer.find\_spec() not found; falling back to find\_module()

FAILED tests/test\_with\_weaver.py::test\_weave\_fixture - ImportWarning: PluginImportFixer.find\_spec() not found; falling back to find\_module()

FAILED tests/test\_with\_weaver.py::test\_weave\_method - ImportWarning: PluginImportFixer.find\_spec() not found; falling back to find\_module()

ERROR tests/test\_with\_testcase.py::TerribleTerribleWayToWritePatchTests::test\_foo2 - pytest\_benchmark.logger.PytestBenchmarkWarning: Benchmark fixture was not used at all in this test!

ERROR tests/test\_with\_weaver.py::test\_weave\_fixture - pytest\_benchmark.logger.PytestBenchmarkWarning: Benchmark fixture was not used at all in this test!

ERROR tests/test\_with\_weaver.py::test\_weave\_method - pytest\_benchmark.logger.PytestBenchmarkWarning: Benchmark fixture was not used at all in this test!

=========================== 4 failed, 215 passed, 19 skipped, 3 errors in 921.18s (0:15:21) ============================



\## Cobertura de código



Commando executado:



```bash

pytest --cov=pytest\_benchmark --cov-report=term-missing --cov-report=html --cov-report=xml -o addopts=""



\## Resultado:



Arquivos gerados:



coverage.xml

htmlcov/index.html



A cobertura foi gerada usando pytest-cov.

## GitHub Actions

Foi configurada uma pipeline no GitHub Actions para executar automaticamente:

- instalação das dependências;
- testes com pytest;
- geração de cobertura em XML.

Arquivo configurado:

- `.github/workflows/tests.yml`
