import os
import subprocess
import tempfile

import pytest
from example_apps import get_apps, reruns, reruns_delay, validate_example
from playwright.sync_api import Page

from shiny._main_create import (
    GithubRepoLocation,
    parse_github_arg,
    shiny_internal_templates,
)


def subprocess_create(
    app_template: str,
    dest_dir: str = "",
    *,
    mode: str = "core",
    package_name: str = "",
):
    cmd = [
        "shiny",
        "create",
        "--template",
        app_template,
        "--mode",
        mode,
        "--dir",
        dest_dir,
        "--package-name",
        package_name,
    ]

    subprocess.run(cmd)
    assert os.path.isdir(dest_dir)

    # Package templates don't have a top-level app.py file
    if package_name == "":
        assert os.path.isfile(f"{dest_dir}/app.py")
    else:
        assert os.path.isfile(f"{dest_dir}/pyproject.toml")

    print("\nCheck for duplicate files")
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run(cmd, check=True)


@pytest.mark.flaky(reruns=reruns, reruns_delay=reruns_delay)
@pytest.mark.parametrize("ex_app_path", get_apps("shiny/templates/app"))
def test_template_examples(page: Page, ex_app_path: str) -> None:
    validate_example(page, ex_app_path)


app_templates = [t.id for t in shiny_internal_templates.apps]
pkg_templates = [t.id for t in shiny_internal_templates.packages]
assert len(app_templates) > 0
assert len(pkg_templates) > 0


@pytest.mark.flaky(reruns=reruns, reruns_delay=reruns_delay)
@pytest.mark.parametrize("app_template", app_templates)
def test_create_core(app_template: str, page: Page):
    with tempfile.TemporaryDirectory("example_apps") as tmpdir:
        subprocess_create(app_template, dest_dir=tmpdir)
        validate_example(page, f"{tmpdir}/app.py")


@pytest.mark.flaky(reruns=reruns, reruns_delay=reruns_delay)
@pytest.mark.parametrize("app_template", ["basic-app"])
def test_create_express(app_template: str, page: Page):
    with tempfile.TemporaryDirectory("example_apps") as tmpdir:
        subprocess_create(app_template, dest_dir=tmpdir, mode="express")
        validate_example(page, f"{tmpdir}/app.py")


@pytest.mark.flaky(reruns=reruns, reruns_delay=reruns_delay)
@pytest.mark.parametrize("app_template", pkg_templates)
def test_create_js(app_template: str):
    with tempfile.TemporaryDirectory("example_apps") as tmpdir:
        subprocess_create(app_template, dest_dir=tmpdir, package_name="my_component")
        # TODO-Karan: Add test to validate once flag to install packages is implemented


def test_parse_github_arg():
    expected = GithubRepoLocation(
        repo_owner="posit-dev",
        repo_name="py-shiny",
        ref="main",
        path="shiny/templates/app/basic-app",
    )

    # * {repo_owner}/{repo_name}@{ref}:{path}
    actual_ref_path = parse_github_arg(
        "posit-dev/py-shiny@main:shiny/templates/app/basic-app"
    )
    assert actual_ref_path == expected

    # * {repo_owner}/{repo_name}:{path}@{ref}
    actual_path_ref = parse_github_arg(
        "posit-dev/py-shiny:shiny/templates/app/basic-app@main"
    )
    assert actual_path_ref == expected

    # * {repo_owner}/{repo_name}/{path}@{ref}
    actual_path_slash_ref = parse_github_arg(
        "posit-dev/py-shiny/shiny/templates/app/basic-app@main"
    )
    assert actual_path_slash_ref == expected

    # * {repo_owner}/{repo_name}/{path}?ref={ref}
    actual_path_slash_query = parse_github_arg(
        "posit-dev/py-shiny/shiny/templates/app/basic-app?ref=main"
    )
    assert actual_path_slash_query == expected

    actual_path_full = parse_github_arg(
        "https://github.com/posit-dev/py-shiny/tree/main/shiny/templates/app/basic-app"
    )
    assert actual_path_full == expected

    actual_path_part = parse_github_arg(
        "github.com/posit-dev/py-shiny/tree/main/shiny/templates/app/basic-app"
    )
    assert actual_path_part == expected

    # REF is implied, defaults to HEAD
    expected.ref = "HEAD"

    # * {repo_owner}/{repo_name}:{path}
    actual_path_colon = parse_github_arg(
        "posit-dev/py-shiny:shiny/templates/app/basic-app"
    )
    assert actual_path_colon == expected

    # * {repo_owner}/{repo_name}/{path}
    actual_path_slash = parse_github_arg(
        "posit-dev/py-shiny/shiny/templates/app/basic-app"
    )
    assert actual_path_slash == expected

    # complicated ref
    actual_ref_tag = parse_github_arg(
        "posit-dev/py-shiny@v0.1.0:shiny/templates/app/basic-app"
    )
    expected.ref = "v0.1.0"
    assert actual_ref_tag == expected

    actual_ref_branch = parse_github_arg(
        "posit-dev/py-shiny@feat/new-template:shiny/templates/app/basic-app"
    )
    expected.ref = "feat/new-template"
    assert actual_ref_branch == expected
