project = "pulseio"
copyright = "2026, Nicholas Silva"  # noqa: A001
author = "Nicholas Silva"

version = ""
release = ""

extensions = ["sphinx.ext.autodoc"]
autodoc_member_order = "bysource"

templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = None

html_theme = "alabaster"
html_theme_options = {
    "github_user": "Robotz213",
    "github_repo": "PulseIo",
    "github_banner": True,
    "github_button": True,
    "github_type": "star",
    "fixed_sidebar": True,
}
htmlhelp_basename = "pulseiodoc"

latex_elements = {}
latex_documents = [
    (master_doc, "pulseio.tex", "pulseio Documentation", author, "manual"),
]

man_pages = [(master_doc, "pulseio", "pulseio Documentation", [author], 1)]

texinfo_documents = [
    (
        master_doc,
        "pulseio",
        "pulseio Documentation",
        author,
        "pulseio",
        "Async Socket.IO integration for Quart applications.",
        "Miscellaneous",
    ),
]

epub_title = project
epub_exclude_files = ["search.html"]
