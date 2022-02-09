"""UI Toolkit for Shiny."""

# All objects imported into this scope will be available as shiny.ui.foo
from ._bootstrap import *
from ._download_button import *
from ._html_dependencies import *
from ._input_action_button import *
from ._input_check_radio import *
from ._input_date import *
from ._input_file import *
from ._input_numeric import *
from ._input_password import *
from ._input_select import *
from ._input_slider import *
from ._input_text import *
from ._input_update import *
from ._insert import *
from ._modal import *
from ._navs import *
from ._notification import *
from ._output import *
from ._page import *
from ._progress import *
from htmltools import TagList, Tag, TagChildArg, TagAttrArg, tags, HTML, head_content

# "Re-export" top-level tags
# Note this should match https://github.com/rstudio/py-htmltools/blob/dcebb4/htmltools/tags.py#L8-L26
# but we hard-code it here so
from htmltools import (
    p,
    h1,
    h2,
    h3,
    h4,
    h5,
    h6,
    a,
    br,
    div,
    span,
    pre,
    code,
    img,
    strong,
    em,
    hr,
)
