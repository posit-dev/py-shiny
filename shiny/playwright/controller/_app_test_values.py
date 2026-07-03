from __future__ import annotations

from typing import Any, Literal

from playwright.sync_api import Page

from ..expect._expect_to_change import retry_with_timeout

__all__ = ("AppTestValues",)

_DEFAULT_TIMEOUT_SECS = 30


class AppTestValues:
    """
    Read a Shiny session's test-mode snapshot of `input`, `output`, and `export`
    values from a running app.

    Requires the app to be running in test mode (construct the app with
    `App(test_mode=True)` or set the `SHINY_TESTMODE=1` environment variable);
    otherwise the snapshot endpoint is not served and the methods raise a
    `RuntimeError`. The pytest app-launch fixtures (`local_app`,
    `create_app_fixture`) enable test mode by default.

    The snapshot URL is discovered from the Shiny client itself
    (`window.Shiny.shinyapp.getTestSnapshotBaseUrl(...)`) and fetched over HTTP, so
    the app must be loaded in the page before these methods are called.

    Examples
    --------
    ```python
    from shiny.playwright import controller

    app_values = controller.AppTestValues(page)
    app_values.expect_input("name", "abc")
    app_values.expect_output("greeting", "Hello abc")
    app_values.expect_export("upper", "ABC")
    snapshot = app_values.get()  # {"input": {...}, "output": {...}, "export": {...}}
    ```
    """

    page: Page
    """Playwright `Page` of the Shiny app."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def _fetch(self) -> dict[str, Any]:
        # Discover the snapshot URL from the Shiny client. Optional chaining keeps
        # `evaluate` from throwing when the client API isn't present yet (app not
        # loaded/bound); the try/except covers any other page-level error. Either
        # way we raise a clear message instead of an opaque Playwright/URL error.
        try:
            url = self.page.evaluate(
                "() => window.Shiny?.shinyapp?.getTestSnapshotBaseUrl?."
                "({ fullUrl: true }) ?? null"
            )
        except Exception as e:
            raise RuntimeError(
                "Could not read the test-mode snapshot URL from the page. Make sure "
                "the Shiny app is loaded and bound before using `AppTestValues` "
                "(e.g. `page.goto(app.url)` and wait for an element to appear)."
            ) from e
        if not url:
            raise RuntimeError(
                "The Shiny client API `window.Shiny.shinyapp.getTestSnapshotBaseUrl` "
                "was not available. Ensure the app is fully loaded and bound in the "
                "page before reading the test-mode snapshot."
            )
        url = str(url)
        response = self.page.request.get(url)
        if not response.ok:
            raise RuntimeError(
                f"Test-mode snapshot request to {url} returned HTTP "
                f"{response.status}. Enable test mode via `App(test_mode=True)` or "
                f"the `SHINY_TESTMODE=1` environment variable."
            )
        try:
            return response.json()
        except Exception as e:
            # A 200 with a non-JSON body (e.g. an HTML error page from a proxy)
            # would otherwise surface as an opaque decode error.
            raise RuntimeError(
                f"Test-mode snapshot request to {url} returned a non-JSON body "
                f"(HTTP {response.status})."
            ) from e

    def get(self) -> dict[str, Any]:
        """
        Return the raw test-mode snapshot.

        Returns
        -------
        :
            A dict with `"input"`, `"output"`, and `"export"` keys, each mapping
            (namespaced) ids to their JSON-decoded values. Performs a single fetch
            (no retry).
        """
        return self._fetch()

    def _expect_value(
        self, block: str, key: str, value: Any, timeout: float | None
    ) -> None:
        @retry_with_timeout(timeout if timeout is not None else _DEFAULT_TIMEOUT_SECS)
        def _() -> None:
            section = self._fetch()[block]
            if key not in section:
                raise AssertionError(
                    f"{block}[{key!r}] is not present in the test snapshot. "
                    f"Present keys: {sorted(section)}"
                )
            actual = section[key]
            if actual != value:
                raise AssertionError(
                    f"{block}[{key!r}] == {actual!r}, expected {value!r}"
                )

        _()

    def expect_input(
        self, key: str, value: Any, *, timeout: float | None = None
    ) -> None:
        """
        Expect the input `key` to equal `value` (JSON-decoded), retrying until it
        matches or `timeout` seconds elapse.
        """
        self._expect_value("input", key, value, timeout)

    def expect_output(
        self, key: str, value: Any, *, timeout: float | None = None
    ) -> None:
        """
        Expect the output `key` to equal `value` (JSON-decoded), retrying until it
        matches or `timeout` seconds elapse.
        """
        self._expect_value("output", key, value, timeout)

    def expect_export(
        self, key: str, value: Any, *, timeout: float | None = None
    ) -> None:
        """
        Expect the exported value `key` to equal `value` (JSON-decoded), retrying
        until it matches or `timeout` seconds elapse.
        """
        self._expect_value("export", key, value, timeout)

    def _expect_values(
        self,
        block: str,
        values: dict[str, Any],
        match: Literal["subset", "exact"],
        timeout: float | None,
    ) -> None:
        if match not in ("subset", "exact"):
            raise ValueError(f"`match` must be 'subset' or 'exact', not {match!r}.")

        @retry_with_timeout(timeout if timeout is not None else _DEFAULT_TIMEOUT_SECS)
        def _() -> None:
            section = self._fetch()[block]

            # Keys expected but absent (both modes) and, for "exact" only, keys
            # present in the snapshot that were not expected.
            missing = sorted(set(values) - set(section))
            extra = sorted(set(section) - set(values)) if match == "exact" else []
            # Value mismatches, checked for every expected key that is present.
            # This applies to BOTH modes: "exact" must verify values too, not
            # just that the key sets are equal.
            mismatched = sorted(
                key for key in values if key in section and section[key] != values[key]
            )

            if not (missing or extra or mismatched):
                return

            problems: list[str] = []
            if missing:
                problems.append(f"missing keys {missing}")
            if extra:
                problems.append(f"unexpected keys {extra}")
            problems += [
                f"{block}[{key!r}] == {section[key]!r}, expected {values[key]!r}"
                for key in mismatched
            ]
            raise AssertionError(f"{block} (match={match!r}): " + "; ".join(problems))

        _()

    def expect_inputs(
        self,
        values: dict[str, Any],
        *,
        match: Literal["subset", "exact"] = "subset",
        timeout: float | None = None,
    ) -> None:
        """
        Expect the `input` block to contain `values` (JSON-decoded), retrying until
        it matches or `timeout` seconds elapse.

        Parameters
        ----------
        values
            A mapping of (namespaced) input ids to their expected values.
        match
            `"subset"` (the default) requires every key in `values` to be present
            and equal, ignoring any additional keys in the snapshot. `"exact"`
            additionally requires the snapshot's key set to equal `values`' keys.
        timeout
            Seconds to retry before failing.
        """
        self._expect_values("input", values, match, timeout)

    def expect_outputs(
        self,
        values: dict[str, Any],
        *,
        match: Literal["subset", "exact"] = "subset",
        timeout: float | None = None,
    ) -> None:
        """
        Expect the `output` block to contain `values` (JSON-decoded), retrying until
        it matches or `timeout` seconds elapse.

        Parameters
        ----------
        values
            A mapping of (namespaced) output ids to their expected values.
        match
            `"subset"` (the default) requires every key in `values` to be present
            and equal, ignoring any additional keys in the snapshot. `"exact"`
            additionally requires the snapshot's key set to equal `values`' keys.
        timeout
            Seconds to retry before failing.
        """
        self._expect_values("output", values, match, timeout)

    def expect_exports(
        self,
        values: dict[str, Any],
        *,
        match: Literal["subset", "exact"] = "subset",
        timeout: float | None = None,
    ) -> None:
        """
        Expect the `export` block to contain `values` (JSON-decoded), retrying until
        it matches or `timeout` seconds elapse.

        Parameters
        ----------
        values
            A mapping of (namespaced) exported names to their expected values.
        match
            `"subset"` (the default) requires every key in `values` to be present
            and equal, ignoring any additional keys in the snapshot. `"exact"`
            additionally requires the snapshot's key set to equal `values`' keys.
        timeout
            Seconds to retry before failing.
        """
        self._expect_values("export", values, match, timeout)
