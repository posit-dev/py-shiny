"""Tests for shiny.ui HTML dependencies."""

from htmltools import HTMLDependency

from shiny.ui._html_deps_external import (
    bootstrap_deps,
    ionrangeslider_deps,
    datepicker_deps,
    selectize_deps,
    jqui_deps,
)
from shiny.ui._html_deps_shinyverse import (
    fill_dependency,
    components_dependencies,
)


class TestBootstrapDeps:
    """Tests for bootstrap_deps function."""

    def test_bootstrap_deps_returns_list(self):
        """Test bootstrap_deps returns a list."""
        deps = bootstrap_deps()
        assert isinstance(deps, list)
        assert len(deps) >= 2  # jQuery and Bootstrap

    def test_bootstrap_deps_with_css(self):
        """Test bootstrap_deps includes CSS by default."""
        deps = bootstrap_deps(include_css=True)
        bootstrap_dep = deps[1]  # First is jQuery, second is Bootstrap
        assert bootstrap_dep.stylesheet is not None

    def test_bootstrap_deps_without_css(self):
        """Test bootstrap_deps can exclude CSS."""
        deps = bootstrap_deps(include_css=False)
        bootstrap_dep = deps[1]
        # Returns empty list when CSS is excluded
        assert not bootstrap_dep.stylesheet


class TestIonRangeSliderDeps:
    """Tests for ionrangeslider_deps function."""

    def test_ionrangeslider_deps_returns_list(self):
        """Test ionrangeslider_deps returns a list."""
        deps = ionrangeslider_deps()
        assert isinstance(deps, list)
        assert len(deps) == 2  # ionrangeslider and strftime

    def test_ionrangeslider_deps_with_css(self):
        """Test ionrangeslider_deps includes CSS by default."""
        deps = ionrangeslider_deps(include_css=True)
        assert deps[0].stylesheet is not None

    def test_ionrangeslider_deps_without_css(self):
        """Test ionrangeslider_deps can exclude CSS."""
        deps = ionrangeslider_deps(include_css=False)
        # Returns empty list when CSS is excluded
        assert not deps[0].stylesheet


class TestDatepickerDeps:
    """Tests for datepicker_deps function."""

    def test_datepicker_deps_returns_dependency(self):
        """Test datepicker_deps returns an HTMLDependency."""
        dep = datepicker_deps()
        assert isinstance(dep, HTMLDependency)
        assert dep.name == "bootstrap-datepicker"

    def test_datepicker_deps_with_css(self):
        """Test datepicker_deps includes CSS by default."""
        dep = datepicker_deps(include_css=True)
        assert dep.stylesheet is not None

    def test_datepicker_deps_without_css(self):
        """Test datepicker_deps can exclude CSS."""
        dep = datepicker_deps(include_css=False)
        # Returns empty list when CSS is excluded
        assert not dep.stylesheet


class TestSelectizeDeps:
    """Tests for selectize_deps function."""

    def test_selectize_deps_returns_dependency(self):
        """Test selectize_deps returns an HTMLDependency."""
        dep = selectize_deps()
        assert isinstance(dep, HTMLDependency)
        assert dep.name == "selectize"

    def test_selectize_deps_with_css(self):
        """Test selectize_deps includes CSS by default."""
        dep = selectize_deps(include_css=True)
        assert dep.stylesheet is not None

    def test_selectize_deps_without_css(self):
        """Test selectize_deps can exclude CSS."""
        dep = selectize_deps(include_css=False)
        # Returns empty list when CSS is excluded
        assert not dep.stylesheet


class TestJquiDeps:
    """Tests for jqui_deps function."""

    def test_jqui_deps_returns_dependency(self):
        """Test jqui_deps returns an HTMLDependency."""
        dep = jqui_deps()
        assert isinstance(dep, HTMLDependency)
        assert dep.name == "jquery-ui"


class TestFillDependency:
    """Tests for fill_dependency function."""

    def test_fill_dependency_returns_dependency(self):
        """Test fill_dependency returns an HTMLDependency."""
        dep = fill_dependency()
        assert isinstance(dep, HTMLDependency)
        assert dep.name == "htmltools-fill"


class TestComponentsDependencies:
    """Tests for components_dependencies function."""

    def test_components_dependencies_returns_dependency(self):
        """Test components_dependencies returns an HTMLDependency."""
        dep = components_dependencies()
        assert isinstance(dep, HTMLDependency)
        assert dep.name == "bslib-components"

    def test_components_dependencies_with_css(self):
        """Test components_dependencies includes CSS by default."""
        dep = components_dependencies(include_css=True)
        assert dep.stylesheet is not None

    def test_components_dependencies_without_css(self):
        """Test components_dependencies can exclude CSS."""
        dep = components_dependencies(include_css=False)
        # Returns empty list when CSS is excluded
        assert not dep.stylesheet
