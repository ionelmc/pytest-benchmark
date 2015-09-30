# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinxcontrib.napoleon'
]
if os.getenv('SPELLCHECK'):
    extensions += 'sphinxcontrib.spelling',
    spelling_show_suggestions = True
    spelling_lang = 'en_US'

source_suffix = '.rst'
master_doc = 'index'
project = 'pytest-benchmark'
year = '2014-2015'
author = 'Ionel Cristian Mărieș'
copyright = '{0}, {1}'.format(year, author)
version = release = '3.0.0a2'
html_theme = "sphinx_py3doc_enhanced_theme"

pygments_style = 'trac'
templates_path = ['.']
html_use_smartypants = True
html_last_updated_fmt = '%b %d, %Y'
html_split_index = True
html_sidebars = {
   '**': ['searchbox.html', 'globaltoc.html', 'sourcelink.html'],
}
html_short_title = '%s-%s' % (project, version)
html_theme_options = {
    'githuburl': 'https://github.com/ionelmc/pytest-benchmark/',
    'appendcss': '''
        div.body code.descclassname { display: none }
        div.body #pedantic-mode code.descclassname { display: inline-block }
    ''',
}
