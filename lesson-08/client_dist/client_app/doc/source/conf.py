# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

path = os.path.dirname(os.path.dirname(os.path.abspath('.')))
sys.path.insert(0, os.path.dirname(path))
sys.path.insert(1, path)
sys.path.insert(1, os.path.join(path, 'logs'))
sys.path.insert(1, os.path.join(path, 'common'))
sys.path.insert(1, os.path.join(path, 'db'))
sys.path.insert(1, os.path.join(path, 'view'))

print(sys.path)

project = 'MMMMonsterChat client'
copyright = '2022, KTo'
author = 'KTo'
release = '1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
]

templates_path = ['_templates']
exclude_patterns = []

language = 'ru'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
