from shinychat import MarkdownStream, output_markdown_stream
from shinychat.express import MarkdownStream as ExpressMarkdownStream

from .._docstring import add_example

__all__ = (
    "output_markdown_stream",
    "MarkdownStream",
    "ExpressMarkdownStream",
)

MarkdownStream = add_example(
    app_file="app-core.py",
    ex_dir="../shiny/api-examples/MarkdownStream",
)(MarkdownStream)

ExpressMarkdownStream = add_example(
    app_file="app-express.py",
    ex_dir="../shiny/api-examples/MarkdownStream",
)(ExpressMarkdownStream)

output_markdown_stream = add_example(
    app_file="app-core.py",
    ex_dir="../shiny/api-examples/MarkdownStream",
)(output_markdown_stream)
