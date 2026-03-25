"""Test all shinylive Python examples on a given site for console errors.

Usage:
    python test_shinylive_site.py <base_url> [output_json]

Examples:
    python test_shinylive_site.py "https://posit-dev.github.io/shinylive/py/examples/"
    python test_shinylive_site.py "https://shinylive.io/py/examples/"
"""

import asyncio
import json
import subprocess
import sys
import time

from playwright.async_api import async_playwright

CACHE_BUSTER = str(int(time.time()))
MIN_EXAMPLES = 50


def fetch_examples() -> list[str]:
    """Dynamically fetch the list of Python examples from the shinylive repo."""
    result = subprocess.run(
        ["gh", "api", "repos/posit-dev/shinylive/contents/examples/python",
         "--jq", ".[].name"],
        capture_output=True, text=True, check=True,
    )
    examples = sorted(line.strip() for line in result.stdout.strip().splitlines() if line.strip())
    assert len(examples) >= MIN_EXAMPLES, (
        f"Expected at least {MIN_EXAMPLES} examples, but found {len(examples)}. "
        f"Check the shinylive repo for issues."
    )
    return examples


async def test_example(browser, base_url, example_name, timeout_ms=45000):
    """Test a single shinylive example in a fresh context (no cache)."""
    # Fresh browser context = no cached data
    context = await browser.new_context()
    page = await context.new_page()
    errors = []

    def on_console(msg):
        if msg.type == "error":
            text = msg.text
            if any(skip in text for skip in [
                "favicon.ico",
                "Failed to load resource",
                "net::ERR_",
                "ResizeObserver",
            ]):
                return
            errors.append(text)

    page.on("console", on_console)

    # Cache-busting query param
    url = f"{base_url}?v={CACHE_BUSTER}#{example_name}"
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        await asyncio.sleep(20)

        try:
            frame_locator = page.frame_locator("iframe")
            body_text = await frame_locator.locator("body").inner_text(timeout=5000)
            if "Traceback (most recent call last)" in body_text:
                errors.append(f"Python traceback in output: {body_text[:300]}")
        except Exception:
            pass

    except Exception as e:
        errors.append(f"Navigation error: {e}")
    finally:
        await page.close()
        await context.close()

    status = "ERROR" if errors else "OK"
    return example_name, status, errors


async def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    base_url = sys.argv[1].rstrip("/") + "/"
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    print("Fetching example list from GitHub...", flush=True)
    examples = fetch_examples()

    print(f"Testing site: {base_url}")
    print(f"Cache buster: ?v={CACHE_BUSTER}")
    print(f"Examples: {len(examples)}\n")

    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        batch_size = 5
        for i in range(0, len(examples), batch_size):
            batch = examples[i : i + batch_size]
            print(f"Testing batch {i // batch_size + 1}: {', '.join(batch)}...", flush=True)
            tasks = [test_example(browser, base_url, name) for name in batch]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)

        await browser.close()

    output = []
    for name, status, errors in results:
        output.append({
            "example": name,
            "url": f"{base_url}#{name}",
            "status": status,
            "errors": errors,
        })

    if output_path:
        with open(output_path, "w") as f:
            json.dump(output, f, indent=2)

    ok = sum(1 for r in results if r[1] == "OK")
    err = sum(1 for r in results if r[1] == "ERROR")
    print(f"\n{'='*60}")
    print(f"Site: {base_url}")
    print(f"Results: {ok} passed, {err} errors out of {len(results)} examples")
    print(f"{'='*60}")

    if err > 0:
        print("\nFailed examples:")
        for name, status, errors in results:
            if status == "ERROR":
                print(f"\n  {name}: {base_url}#{name}")
                for e in errors:
                    print(f"    - {e[:200]}")

    return 1 if err > 0 else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
