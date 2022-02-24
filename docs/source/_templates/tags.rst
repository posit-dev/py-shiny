{{ fullname | escape | underline}}

.. automodule:: {{fullname}}

.. autosummary::
    :toctree:
    :template: tag_func.rst

    {% block functions %}
    {% for item in functions %}
    ~{{ fullname }}.{{ item }}
    {%- endfor %}
    {% endblock %}
