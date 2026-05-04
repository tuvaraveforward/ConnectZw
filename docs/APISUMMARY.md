API Summary — Project1

This file gives a surface-level map of the project's Python modules and where to look for important code.

Top-level utilities and scripts

- manage.py — Django management entrypoint.
- Several helper scripts at repo root (create_admin.py, create_sample_locations.py, verify_*.py, debug_*.py, test_*.py).

Project-level package

- Project1/
  - settings.py — Django settings.
  - urls.py, wsgi.py, asgi.py — Django boot files.
  - email_utils.py, aes_utils.py, encrypted_field.py — utilities.

Apps (high-level)

- Admin/ — admin interface, views, utilities, forms, models, migrations.
- Client/ — client-facing models, views, tasks, tests, ai_services.
- Dealer/ — dealer models, views, forms, tests.
- Location/ — location models, views, filters, tests.
- Pos/ — point-of-sale models and views.

For each app, look in the app folder for these files:

- `models.py` — database models and fields.
- `views.py` — request handling and view logic.
- `forms.py` — Django forms and validation.
- `admin.py` — admin customizations.
- `tests.py` — unit/integration tests.
- `migrations/` — database schema migrations.

Suggested next actions (I can do these for you)

- Extract top-level docstrings and generate per-module markdown under `docs/`.
- Create `docs/Admin.md`, `docs/Client.md`, etc., with exported classes/functions and short descriptions.
- Run `pdoc` or `sphinx-apidoc` to generate full API docs and copy them into `docs/_site`.

If you want, I can now:

- Generate per-app markdown files listing each module's classes and functions (extracting docstrings).
- Or scaffold a Sphinx setup and generate HTML docs.

Tell me which of those you prefer and I'll continue.