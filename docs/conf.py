# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sphinx_py3doc_enhanced_theme

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.extlinks',
    'sphinx.ext.ifconfig',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
]
source_suffix = '.rst'
master_doc = 'index'
project = 'pytest-benchmark'
year = '2014-2021'
author = 'Ionel Cristian Mărieș'
copyright = '{0}, {1}'.format(year, author)
version = release = '3.4.0'

pygments_style = 'trac'
templates_path = ['.']
extlinks = {
    'issue': ('https://github.com/ionelmc/pytest-benchmark/issues/%s', '#'),
    'pr': ('https://github.com/ionelmc/pytest-benchmark/pull/%s', 'PR #'),
}
html_theme = "sphinx_py3doc_enhanced_theme"
html_theme_path = [sphinx_py3doc_enhanced_theme.get_html_theme_path()]
html_theme_options = {
    'githuburl': 'https://github.com/ionelmc/pytest-benchmark/',
    'appendcss': '''
        div.body code.descclassname { display: none }
        div.body #pedantic-mode code.descclassname { display: inline-block }
    ''',
}

html_use_smartypants = True
html_last_updated_fmt = '%b %d, %Y'
html_split_index = False
html_sidebars = {
   '**': ['searchbox.html', 'globaltoc.html', 'sourcelink.html'],
}
html_short_title = '%s-%s' % (project, version)

napoleon_use_ivar = True
napoleon_use_rtype = False
napoleon_use_param = False
