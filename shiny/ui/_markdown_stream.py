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
    example_name="MarkdownStream",
)(MarkdownStream)

ExpressMarkdownStream = add_example(
    app_file="app-express.py",
    example_name="MarkdownStream",
)(ExpressMarkdownStream)

output_markdown_stream = add_example(
    app_file="app-core.py",
    example_name="MarkdownStream",
)(output_markdown_stream)
