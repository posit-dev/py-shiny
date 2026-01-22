"""Tests for shiny.ui._html_deps_external module."""

from htmltools import HTMLDependency

from shiny._versions import bootstrap as bootstrap_version
from shiny.ui._html_deps_external import (
    bootstrap_deps,
    datepicker_deps,
    ionrangeslider_deps,
    jqui_deps,
    selectize_deps,
)


class TestBootstrapDeps:
    """Tests for bootstrap_deps function."""

    def test_bootstrap_deps_returns_list(self):
        """bootstrap_deps should return a list."""
        result = bootstrap_deps()
        assert isinstance(result, list)

    def test_bootstrap_deps_contains_dependencies(self):
        """bootstrap_deps should contain HTMLDependency objects."""
        result = bootstrap_deps()
        for dep in result:
            assert isinstance(dep, HTMLDependency)

    def test_bootstrap_deps_includes_jquery(self):
        """bootstrap_deps should include jQuery dependency."""
        result = bootstrap_deps()
        dep_names = [dep.name for dep in result]
        assert "jquery" in dep_names

    def test_bootstrap_deps_includes_bootstrap(self):
        """bootstrap_deps should include bootstrap dependency."""
        result = bootstrap_deps()
        dep_names = [dep.name for dep in result]
        assert "bootstrap" in dep_names

    def test_bootstrap_deps_has_correct_version(self):
        """bootstrap_deps should have correct bootstrap version."""
        result = bootstrap_deps()
        bootstrap_dep = next(dep for dep in result if dep.name == "bootstrap")
        assert str(bootstrap_dep.version) == bootstrap_version

    def test_bootstrap_deps_with_css(self):
        """bootstrap_deps should include CSS by default."""
        result = bootstrap_deps(include_css=True)
        bootstrap_dep = next(dep for dep in result if dep.name == "bootstrap")
        # The dependency should have stylesheet
        assert bootstrap_dep is not None

    def test_bootstrap_deps_without_css(self):
        """bootstrap_deps should work without CSS."""
        result = bootstrap_deps(include_css=False)
        # Should still have dependencies
        assert len(result) >= 2


class TestIonrangesliderDeps:
    """Tests for ionrangeslider_deps function."""

    def test_ionrangeslider_deps_returns_list(self):
        """ionrangeslider_deps should return a list."""
        result = ionrangeslider_deps()
        assert isinstance(result, list)

    def test_ionrangeslider_deps_contains_dependencies(self):
        """ionrangeslider_deps should contain HTMLDependency objects."""
        result = ionrangeslider_deps()
        for dep in result:
            assert isinstance(dep, HTMLDependency)

    def test_ionrangeslider_deps_includes_ionrangeslider(self):
        """ionrangeslider_deps should include ionrangeslider dependency."""
        result = ionrangeslider_deps()
        dep_names = [dep.name for dep in result]
        assert "ionrangeslider" in dep_names

    def test_ionrangeslider_deps_includes_strftime(self):
        """ionrangeslider_deps should include strftime dependency."""
        result = ionrangeslider_deps()
        dep_names = [dep.name for dep in result]
        assert "strftime" in dep_names

    def test_ionrangeslider_deps_has_correct_version(self):
        """ionrangeslider_deps should have correct version."""
        result = ionrangeslider_deps()
        ion_dep = next(dep for dep in result if dep.name == "ionrangeslider")
        assert str(ion_dep.version) == "2.3.1"


class TestDatepickerDeps:
    """Tests for datepicker_deps function."""

    def test_datepicker_deps_returns_dependency(self):
        """datepicker_deps should return an HTMLDependency."""
        result = datepicker_deps()
        assert isinstance(result, HTMLDependency)

    def test_datepicker_deps_has_correct_name(self):
        """datepicker_deps should have correct name."""
        result = datepicker_deps()
        assert result.name == "bootstrap-datepicker"

    def test_datepicker_deps_has_correct_version(self):
        """datepicker_deps should have correct version."""
        result = datepicker_deps()
        assert str(result.version) == "1.9.0"

    def test_datepicker_deps_with_css(self):
        """datepicker_deps should include CSS by default."""
        result = datepicker_deps(include_css=True)
        assert result is not None

    def test_datepicker_deps_without_css(self):
        """datepicker_deps should work without CSS."""
        result = datepicker_deps(include_css=False)
        assert result is not None


class TestSelectizeDeps:
    """Tests for selectize_deps function."""

    def test_selectize_deps_returns_dependency(self):
        """selectize_deps should return an HTMLDependency."""
        result = selectize_deps()
        assert isinstance(result, HTMLDependency)

    def test_selectize_deps_has_correct_name(self):
        """selectize_deps should have correct name."""
        result = selectize_deps()
        assert result.name == "selectize"

    def test_selectize_deps_has_correct_version(self):
        """selectize_deps should have correct version."""
        result = selectize_deps()
        assert str(result.version) == "0.12.6"

    def test_selectize_deps_with_css(self):
        """selectize_deps should include CSS by default."""
        result = selectize_deps(include_css=True)
        assert result is not None

    def test_selectize_deps_without_css(self):
        """selectize_deps should work without CSS."""
        result = selectize_deps(include_css=False)
        assert result is not None


class TestJquiDeps:
    """Tests for jqui_deps function."""

    def test_jqui_deps_returns_dependency(self):
        """jqui_deps should return an HTMLDependency."""
        result = jqui_deps()
        assert isinstance(result, HTMLDependency)

    def test_jqui_deps_has_correct_name(self):
        """jqui_deps should have correct name."""
        result = jqui_deps()
        assert result.name == "jquery-ui"

    def test_jqui_deps_has_correct_version(self):
        """jqui_deps should have correct version."""
        result = jqui_deps()
        assert str(result.version) == "1.12.1"
