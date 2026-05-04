Project1 — Documentation

Overview

This repository is a Django project. The `docs/` folder contains an initial, high-level overview and an API surface summary to help onboard contributors and generate full docs.

Repository layout (top-level apps)

- Admin
- Client
- Dealer
- Location
- Pos
- Project1 (project-level utilities and settings)

What I added here

- docs/APISUMMARY.md: a generated summary of apps and modules.

Next steps

- Run `pydoc`, `pdoc`, or Sphinx to generate full API docs from docstrings.
- Expand each `docs/<app>.md` with per-module details and examples.

Commands to generate docs (suggested)

- Quick HTML with pdoc:

    pdoc --html --output-dir docs/_site Project1 Admin Client Dealer Location Pos

- Sphinx (recommended for extensive docs):

    python -m pip install sphinx sphinx-autobuild sphinx-rtd-theme
    sphinx-quickstart docs/sphinx
    # add extensions: sphinx.ext.autodoc, sphinx.ext.napoleon
    sphinx-apidoc -o docs/sphinx/source .
    make -C docs/sphinx html

Contact

If you want, I can expand per-app files and extract docstrings into these documents.