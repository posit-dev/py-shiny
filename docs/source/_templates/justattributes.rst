
{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}

    {% block methods %}
    {% endblock %}

    {% block attributes %}
    {% if attributes %}
    .. rubric:: Attributes

    .. autosummary::
    {% for item in attributes %}
        ~{{ name }}.{{ item }}
    {%- endfor %}
    {% endif %}
    {% endblock %}
