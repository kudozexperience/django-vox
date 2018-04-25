# -- Django workaround
# import unittest.mock
# import sys

# MODULES = ['django']
# for mod_name in MODULES:
#     sys.modules[mod_name] = unittest.mock.MagicMock()
import django
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.docs_settings'
django.setup()

# -- Project information -----------------------------------------------------

project = 'Django Courier'
copyright = '2018, Alan Trick'
author = 'Alan Trick'

extensions = [
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

language = None

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

pygments_style = 'sphinx'


# -- Options for HTML output -------------------------------------------------

html_theme = 'classic'
html_static_path = ['_static']
htmlhelp_basename = 'DjangoCourierdoc'

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {}

latex_documents = [
    (master_doc, 'DjangoCourier.tex', 'Django Courier Documentation',
     'Alan Trick', 'manual'),
]


# -- Options for manual page output ------------------------------------------

man_pages = [
    (master_doc, 'djangocourier', 'Django Courier Documentation',
     [author], 1)
]


# -- Options for Texinfo output ----------------------------------------------

texinfo_documents = [
    (master_doc, 'DjangoCourier', 'Django Courier Documentation',
     author, 'DjangoCourier', 'One line description of project.',
     'Miscellaneous'),
]
