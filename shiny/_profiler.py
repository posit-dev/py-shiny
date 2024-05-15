from __future__ import annotations

import contextlib
import sys
from typing import Any, Generator


def check_profiler_dependencies() -> None:
    try:
        import pyinstrument  # pyright: ignore[reportUnusedImport]
    except ImportError:
        print(
            "Error: Profiler is not installed. You can install it with "
            "'pip install shiny[profile]'.",
            file=sys.stderr,
        )
        sys.exit(1)


@contextlib.contextmanager
def profiler() -> Generator[None, Any, None]:
    import base64
    import os
    import time
    import webbrowser
    from urllib.parse import quote_plus

    import pyinstrument

    prof = pyinstrument.Profiler()
    prof.start()

    epoch_time = int(time.time())
    output_filename = f"profile-{epoch_time}.json"
    output_filename_abs = os.path.join(os.getcwd(), output_filename)
    print(f"Profiling to {output_filename_abs}", file=sys.stderr)

    try:
        yield
    finally:
        prof_session = prof.stop()

        import pyinstrument.renderers.speedscope

        renderer = pyinstrument.renderers.speedscope.SpeedscopeRenderer()
        output_str = renderer.render(prof_session)

        with open(output_filename_abs, "w", encoding="utf-8") as f:
            f.write(output_str)

        print(f"Profile saved to {output_filename_abs}", file=sys.stderr)

        b64_str = base64.b64encode(output_str.encode("utf-8")).decode("utf-8")
        data_uri = f"data:application/json;base64,{b64_str}"
        full_url = (
            "https://speedscope.app/#profileURL="
            + quote_plus(data_uri)
            # + "&title="
            # + quote_plus(output_filename)
        )

        webbrowser.open(full_url)
