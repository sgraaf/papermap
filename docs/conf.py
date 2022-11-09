"""Sphinx configuration."""
import os
import sys

sys.path.insert(0, os.path.abspath("../src"))
import papermap  # noqa: E402

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "PaperMap"
copyright = "2019, Steven van de Graaf"
author = "Steven van de Graaf"
release = papermap.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autodoc.typehints",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_copybutton",
    "sphinxext.opengraph",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# auto-generate header anchors
myst_heading_anchors = 3

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "Pillow": ("https://pillow.readthedocs.io/en/stable/", None),
}

# move type hints into the description block, instead of the signature
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
html_theme_options = {
    "top_of_page_button": None,
}
