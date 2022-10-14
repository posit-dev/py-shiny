import mimetypes
from math import ceil
from typing import List
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_file("file1", "Choose a file to upload:", multiple=True),
    ui.input_radio_buttons("type", "Type:", ["Binary", "Text"]),
    ui.output_text_verbatim("file_content"),
)


def server(input, output, session):
    MAX_SIZE = 50000

    @output
    @render.text
    def file_content():
        file_infos = input.file1()
        if not file_infos:
            return

        # file_infos is a list of dicts; each dict represents one file. Example:
        # [
        #   {
        #     'name': 'data.csv',
        #     'size': 2601,
        #     'type': 'text/csv',
        #     'datapath': '/tmp/fileupload-1wnx_7c2/tmpga4x9mps/0.csv'
        #   }
        # ]
        out_str = ""
        for file_info in file_infos:
            out_str += (
                "=" * 47
                + "\n"
                + file_info["name"]
                + "\nMIME type: "
                + str(mimetypes.guess_type(file_info["name"])[0])
            )
            if file_info["size"] > MAX_SIZE:
                out_str += f"\nTruncating at {MAX_SIZE} bytes."

            out_str += "\n" + "=" * 47 + "\n"

            if input.type() == "Text":
                with open(file_info["datapath"], "r") as f:
                    out_str += f.read(MAX_SIZE)
            else:
                with open(file_info["datapath"], "rb") as f:
                    data = f.read(MAX_SIZE)
                    out_str += format_hexdump(data)

        return out_str


def format_hexdump(data: bytes) -> str:
    hex_vals = ["{:02x}".format(b) for b in data]
    hex_vals = group_into_blocks(hex_vals, 16)
    hex_vals = [" ".join(row) for row in hex_vals]
    hex_vals = "\n".join(hex_vals)
    return hex_vals


def group_into_blocks(x: List[str], blocksize: int):
    """
    Given a list, return a list of lists, where the inner lists each have `blocksize`
    elements.
    """
    return [
        x[i * blocksize : (i + 1) * blocksize] for i in range(ceil(len(x) / blocksize))
    ]


app = App(app_ui, server)
