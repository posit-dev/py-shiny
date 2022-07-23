API Reference Intro
===================

This website documents the public API of Shiny (for Python). See the `Getting Started
tutorial <https://shiny.rstudio.com/py/>`_ for
a more approachable introduction to the API. The left-hand sidebar lists the full public
API, without any grouping, but the sections below (linked to the right-hand sidebar)
break it into semantically similar groups. Most of the reference pages include a live
example app at the bottom, or at least mention another page with a relevant example.

We've intentionally designed Shiny's API so that you can ``from shiny import *`` to get
access to most of what you need for most apps without introducing an excessive amount of
namespace pollution. Namely, it gives you:

* User interface (UI/HTML) helpers, available via the ``ui`` subpackage.

  * To avoid clashing with this ``ui`` namespace when you do ``from shiny import *``, you'll want to name you UI object something else, like ``app_ui``.

* Reactive programming utilities, available via the ``reactive`` subpackage.
* Decorators for rendering ``output``, available via the ``render`` subpackage.

  * 3rd party packages that want to implement their own rendering functions are encouraged to use a `@render_foo()` naming convention so users may import with `from mypkg import render_foo`.

* A handful of other things you'll want for most apps (e.g., ``App``, ``Module``, etc).
* If you're using type checking, you'll also want to use the ``Inputs``, ``Outputs``, and ``Session`` Classes
  to type the instances supplied to your server function, for example:

.. shinyeditor::

    from shiny import *

    app_ui = ui.page_fluid(
      ui.input_slider("n", "Value of n", min=1, max=10, value=5),
      ui.output_text("n2")
    )

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @output
        @render.text
        def n2():
            return f"The value of n*2 is {input.n() * 2}"

    app = App(app_ui, server)



API Reference
=============

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
    ui.input_switch
    ui.input_radio_buttons
    ui.input_numeric
    ui.input_text
    ui.input_text_area
    ui.input_password
    ui.input_action_button
    ui.input_action_link


Update inputs
~~~~~~~~~~~~~
Programmatically update input values

.. autosummary::
    :toctree: reference/

    ui.update_select
    ui.update_selectize
    ui.update_slider
    ui.update_date
    ui.update_date_range
    ui.update_checkbox
    ui.update_checkbox_group
    ui.update_switch
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
    ui.nav_control
    ui.nav_spacer
    ui.nav_menu
    ui.navset_tab
    ui.navset_tab_card
    ui.navset_pill
    ui.navset_pill_card
    ui.navset_pill_list


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

    ui.markdown
    ui.insert_ui
    ui.remove_ui


Rendering outputs
~~~~~~~~~~~~~~~~~
UI (`output_*()`) and server (``render``)ing functions for generating content server-side.

.. autosummary::
    :toctree: reference/

    ui.output_plot
    render.plot
    ui.output_image
    render.image
    ui.output_text
    ui.output_text_verbatim
    render.text
    ui.output_ui
    render.ui


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
    reactive.poll
    reactive.file_reader
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

    module.ui
    module.server


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
    reactive.get_current_context
    input_handler.input_handlers
