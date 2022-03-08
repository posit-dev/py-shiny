Shiny for Python API Reference
==============================

* :ref:`search`

.. currentmodule:: shiny

Page containers
~~~~~~~~~~~~~~~
Create a user interface page container.

.. autosummary::
    :toctree: reference/

    ui.page_navbar
    ui.page_fluid
    ui.page_fixed
    ui.page_bootstrap


UI Layout
~~~~~~~~~~
Control the layout of multiple UI components.

.. autosummary::
    :toctree: reference/

    ui.layout_sidebar
    ui.panel_sidebar
    ui.panel_main
    ui.column
    ui.row

UI Inputs
~~~~~~~~~
Create UI that prompts the user for input values or interaction.

.. autosummary::
    :toctree: reference/

    ui.input_select
    ui.input_selectize
    ui.input_slider
    ui.input_date
    ui.input_date_range
    ui.input_checkbox
    ui.input_checkbox_group
    ui.input_radio_buttons
    ui.input_numeric
    ui.input_text
    ui.input_text_area
    ui.input_password
    ui.input_action_button


Update inputs
~~~~~~~~~~~~~
Programmatically update input values

.. autosummary::
    :toctree: reference/

    ui.update_select
    ui.update_slider
    ui.update_date
    ui.update_date_range
    ui.update_checkbox
    ui.update_checkbox_group
    ui.update_radio_buttons
    ui.update_numeric
    ui.update_text
    ui.update_text_area
    ui.update_navs


Navigation (tab) panels
~~~~~~~~~~~~~~~~~~~~~~~
Create segments of UI content.

.. autosummary::
    :toctree: reference/

    ui.nav
    ui.nav_item
    ui.nav_spacer
    ui.nav_menu
    ui.navs_tab
    ui.navs_tab_card
    ui.navs_pill
    ui.navs_pill_card
    ui.navs_pill_list


UI panels
~~~~~~~~~
Visually group together a section of UI components.

.. autosummary::
    :toctree: reference/

    ui.panel_absolute
    ui.panel_fixed
    ui.panel_conditional
    ui.panel_title
    ui.panel_well


Uploads & downloads
~~~~~~~~~~~~~~~~~~~
Allows users to upload and download files.

.. autosummary::
    :toctree: reference/

    ui.input_file
    ui.download_button


Custom UI
~~~~~~~~~
Lower-level UI functions for creating custom HTML/CSS/JS.

.. autosummary::
    :toctree: reference/
    :template: justattributes.rst

    ui.HTML

.. autosummary::
    :toctree: reference/
    :template: class.rst

    ui.TagList

.. autosummary::
    :toctree: reference/
    :template: tags.rst

    ui.tags

.. autosummary::
    :toctree: reference/

    ui.insert_ui
    ui.remove_ui


Rendering outputs
~~~~~~~~~~~~~~~~~
UI (`output_*()`) and server (``render_*()``) functions for generating content server-side.

.. autosummary::
    :toctree: reference/

    ui.output_plot
    render_plot
    ui.output_image
    render_image
    ui.output_text
    ui.output_text_verbatim
    render_text
    ui.output_ui
    render_ui


Reactive programming
~~~~~~~~~~~~~~~~~~~~
Reactive programming facilities for Python.

.. autosummary::
    :toctree: reference/

    reactive.Calc
    reactive.Effect

.. autosummary::
    :toctree: reference/
    :template: class.rst

    reactive.Value

.. autosummary::
    :toctree: reference/

    reactive.isolate
    reactive.invalidate_later
    reactive.flush
    event


Create and run applications
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Create, run, stop, and hook into the lifecycle of Shiny applications.

.. autosummary::
    :toctree: reference/

    run_app

.. autosummary::
    :toctree: reference/
    :template: class.rst

    App
    Inputs
    Outputs
    Session

Display messages
~~~~~~~~~~~~~~~~
Display messages to the user.

.. autosummary::
    :toctree: reference/

    ui.help_text
    ui.notification_show
    ui.notification_remove
    ui.modal
    ui.modal_show
    ui.modal_remove
    ui.modal_button

.. autosummary::
    :toctree: reference/
    :template: class.rst

    ui.Progress

Error validation
~~~~~~~~~~~~~~~~
Control how errors are shown to the user.

.. autosummary::
    :toctree: reference/

    req

.. autosummary::
    :toctree: reference/
    :template: class.rst

    types.SilentException
    types.SilentCancelOutputException
    types.SafeException


Modules
~~~~~~~
Control application complexity by namespacing UI and server code.

.. autosummary::
    :toctree: reference/
    :template: class.rst

    Module


Type hints
~~~~~~~~~~
Classes for type hinting input/output values.

.. autosummary::
    :toctree: reference/
    :template: justattributes.rst

    types.FileInfo
    types.ImgData


Developer facing tools
~~~~~~~~~~~~~~~~~~~~~~~
Tools for Shiny developers.

.. autosummary::
    :toctree: reference/

    session.get_current_session
    session.require_active_session
    session.session_context
    input_handler.input_handlers
