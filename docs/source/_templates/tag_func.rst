..
  This essentially replaces the default behavior of .. autosummary::, which is
  https://raw.githubusercontent.com/sphinx-doc/sphinx/4.x/sphinx/ext/autosummary/templates/autosummary/base.rst
  For whatever reason, that default behavior doesn't work when applied to ui.tags

{{ fullname | escape | underline}}

.. auto{{ objtype }}:: {{ module }}.{{ objname }}
