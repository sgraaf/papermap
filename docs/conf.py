"""Sphinx configuration."""

from __future__ import annotations

from collections import _tuplegetter  # type: ignore[attr-defined]
from importlib import metadata
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.ext.autodoc._property_types import (  # pyrefly: ignore[missing-import], # ty: ignore[unresolved-import]
        _AutodocObjType,
    )

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "papermap"
author = "Steven van de Graaf"
copyright = f"2019, {author}"  # noqa: A001

# The full version, including alpha/beta/rc tags.
release = metadata.version("papermap")
# The short X.Y version.
version = release.rsplit(".", 1)[0]

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autodoc.typehints",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_copybutton",
    "sphinxext.opengraph",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# auto-generate header anchors and suppress header warnings
myst_heading_anchors = 3
suppress_warnings = ["myst.header"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "Pillow": ("https://pillow.readthedocs.io/en/stable/", None),
}

# move type hints into the description block, instead of the signature
autodoc_member_order = "bysource"
autodoc_default_options = {
    "show-inheritance": True,
}
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
html_theme_options: dict[str, Any] = {
    "top_of_page_buttons": [],
}


# -- Hacky fix for autodocumenting `collections.NamedTuple` ------------------
# https://stackoverflow.com/a/70459782
def remove_namedtuple_attrib_docstring(  # noqa: PLR0913, D103
    app: Sphinx,  # noqa: ARG001
    what: _AutodocObjType,  # noqa: ARG001
    name: str,  # noqa: ARG001
    obj: Any,  # noqa: ANN401
    skip: bool,  # noqa: FBT001
    options: Any,  # noqa: ARG001, ANN401
) -> bool:
    if isinstance(obj, _tuplegetter):
        return True
    return skip


def setup(app: Sphinx) -> None:  # noqa: D103
    app.connect("autodoc-skip-member", remove_namedtuple_attrib_docstring)
