# -- Project information -----------------------------------------------------

project = 'Django Courier'
copyright = '2018, Alan Trick'
author = 'Alan Trick'

# The short X.Y version
version = ''
# The full version, including alpha/beta/rc tags
release = '0.5.5'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.doctest',
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
