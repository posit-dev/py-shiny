..
    Derived from the sphinx v3.0.4 source code: sphinx/ext/autosummary/templates/autosummary/class.rst
    This slightly modified version is used to get methods to hyperlink to their own
    reference/ page (i.e., it adds toctree to autosummary) and hides the __init__ method

{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}

    {% block methods %}

    {% if methods %}
    .. rubric:: Methods

    .. autosummary::
        :toctree:
    {% for item in methods %}
    {%- if item not in ['__init__', 'call_pyodide'] %}
        ~{{ name }}.{{ item }}
    {% endif %}
    {%- endfor %}
    {% endif %}
    {% endblock %}

    {% block attributes %}
    {% if attributes %}
    .. rubric:: Attributes

    .. autosummary::
      :toctree:
    {% for item in attributes %}
        ~{{ name }}.{{ item }}
    {%- endfor %}
    {% endif %}
    {% endblock %}
