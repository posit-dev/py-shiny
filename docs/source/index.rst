Shiny for Python API Reference
================

* :ref:`search`


Page containers
~~~~~~~~~~~~~~~

Create a user interface page container.

.. autosummary::
    :toctree: reference/

    ~shiny.ui.page_navbar
    ~shiny.ui.page_fluid
    ~shiny.ui.page_fixed
    ~shiny.ui.page_bootstrap


UI Layout
~~~~~~~~~

Control the layout of multiple UI components.

.. autosummary::
    :toctree: reference/

    ~shiny.ui.layout_sidebar
    ~shiny.ui.panel_sidebar
    ~shiny.ui.panel_main
    ~shiny.ui.column
    ~shiny.ui.row

UI Inputs
~~~~~~~~~

Create UI that prompts the user for input values or interaction.

.. autosummary::
    :toctree: reference/

    ~shiny.ui.input_select
    ~shiny.ui.input_selectize
    ~shiny.ui.input_slider
    ~shiny.ui.input_date
    ~shiny.ui.input_date_range
    ~shiny.ui.input_checkbox
    ~shiny.ui.input_checkbox_group
    ~shiny.ui.input_radio_buttons
    ~shiny.ui.input_numeric
    ~shiny.ui.input_text
    ~shiny.ui.input_text_area
    ~shiny.ui.input_password
    ~shiny.ui.input_action_button


Update inputs
~~~~~~~~~~~~~

Programmatically update input values

.. autosummary::
    :toctree: reference/

    ~shiny.ui.update_select
    ~shiny.ui.update_slider
    ~shiny.ui.update_date
    ~shiny.ui.update_date_range
    ~shiny.ui.update_checkbox
    ~shiny.ui.update_checkbox_group
    ~shiny.ui.update_radio_buttons
    ~shiny.ui.update_numeric
    ~shiny.ui.update_text
    ~shiny.ui.update_text_area
    ~shiny.ui.update_navs


Navigation (tab) panels
~~~~~~~~~~~~~~~~~~~~~~~

Create segments of UI content.

.. autosummary::
    :toctree: reference/

    ~shiny.ui.nav
    ~shiny.ui.nav_item
    ~shiny.ui.nav_spacer
    ~shiny.ui.nav_menu
    ~shiny.ui.navs_tab
    ~shiny.ui.navs_tab_card
    ~shiny.ui.navs_pill
    ~shiny.ui.navs_pill_card
    ~shiny.ui.navs_pill_list


UI panels
~~~~~~~~~

Visually group together a section of UI components.

.. autosummary::
    :toctree: reference/

    ~shiny.ui.panel_absolute
    ~shiny.ui.panel_fixed
    ~shiny.ui.panel_conditional
    ~shiny.ui.panel_title
    ~shiny.ui.panel_well


Uploads & downloads
~~~~~~~~~~~~~~~~~~~

Allows users to upload and download files.

.. autosummary::
    :toctree: reference/

    ~shiny.ui.input_file
    ~shiny.ui.download_button


Custom UI
~~~~~~~~~~

Lower-level UI functions for creating custom HTML/CSS/JS.

.. autosummary::
    :toctree: reference/

    ~shiny.ui.HTML
    ~shiny.ui.tags
    ~shiny.ui.TagList
    ~shiny.ui.insert_ui
    ~shiny.ui.remove_ui


Rendering outputs
~~~~~~~~~~~~~~~~~~

UI (`output_*()`) and server (``render_*()``) functions for generating content server-side.

.. autosummary::
    :toctree: reference/

    ~shiny.ui.output_plot
    ~shiny.render_plot
    ~shiny.ui.output_image
    ~shiny.render_image
    ~shiny.ui.output_text
    ~shiny.ui.output_text_verbatim
    ~shiny.render_text
    ~shiny.ui.output_ui
    ~shiny.render_ui


Reactive programming
~~~~~~~~~~~~~~~~~~

Reactive programming facilities for Python.

.. autosummary::
    :toctree: reference/

    ~shiny.reactive.Calc
    ~shiny.reactive.Effect
    ~shiny.reactive.Value
    ~shiny.reactive.isolate
    ~shiny.reactive.invalidate_later
    ~shiny.reactive.flush
    ~shiny.event


Create and run applications
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create, run, stop, and hook into the lifecycle of Shiny applications.

.. autosummary::
    :toctree: reference/

    ~shiny.App
    ~shiny.run_app

Display messages
~~~~~~~~~~~~~~~~

Display messages to the user.

.. autosummary::
    :toctree: reference/

    ~shiny.ui.help_text
    ~shiny.ui.notification_show
    ~shiny.ui.notification_remove
    ~shiny.ui.Progress
    ~shiny.ui.modal
    ~shiny.ui.modal_show
    ~shiny.ui.modal_remove
    ~shiny.ui.modal_button

Error validation
~~~~~~~~~~~~~~~~

Control how errors are shown to the user.

.. autosummary::
    :toctree: reference/

    ~shiny.req
    ~shiny.types.SilentException
    ~shiny.types.SilentCancelOutputException
    ~shiny.types.SafeException


Modules
~~~~~~~

Control application complexity by namespacing UI and server code.

.. autosummary::
    :toctree: reference/

    ~shiny.modules.Module
    ~shiny.modules.ModuleInputs
    ~shiny.modules.ModuleOutputs
    ~shiny.modules.ModuleSession
