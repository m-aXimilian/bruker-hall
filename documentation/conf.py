# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import mock
sys.path.insert(0, os.path.abspath('../src'))

MOCK_MODULES = ['numpy', 'matplotlib', 'matplotlib.pyplot', 'nidaqmx', 'pyvisa', 'tqdm', 'scipy',
                'numpy.core', 'nidaqmx.constants', 'numpy.core.fromnumeric', 'numpy.lib', 'numpy.lib.index_tricks', 'nidaqmx.task', 'yaml', 'pymeasure.instruments.srs','../fmr-py/src/visa_devices',
                'fmr-py/src/visa_devices', 'visa_devices']

for mod_name in MOCK_MODULES:
    sys.modules[mod_name] = mock.Mock()


# -- Project information -----------------------------------------------------

project = 'Burker Hall Measurements'
copyright = '2022, Maximilian Küffner'
author = 'Maximilian Küffner'

# The full version, including alpha/beta/rc tags
release = '0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.napoleon', 'sphinx.ext.autodoc', 'sphinx.ext.coverage']
napoleon_google_docstring = True
autodoc_default_options = { "members": True, "undoc-members": True, "private-members": True}
# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'agogo'

html_theme_options = {
    
}
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".

