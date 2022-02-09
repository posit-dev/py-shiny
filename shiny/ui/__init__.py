"""UI Toolkit for Shiny."""

# All objects imported into this scope will be available as shiny.ui.foo
from .bootstrap import *
from .download_button import *
from .html_dependencies import *
from .input_action_button import *
from .input_check_radio import *
from .input_date import *
from .input_file import *
from .input_numeric import *
from .input_password import *
from .input_select import *
from .input_slider import *
from .input_text import *
from .input_update import *
from .insert import *
from .modal import *
from .navs import *
from .notification import *
from .output import *
from .page import *
from .progress import *
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
