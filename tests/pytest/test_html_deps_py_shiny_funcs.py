"""Tests for shiny.ui._html_deps_py_shiny module"""

from htmltools import HTMLDependency

from shiny import __version__
from shiny.ui._html_deps_py_shiny import (
    busy_indicators_dep,
    data_frame_deps,
    page_output_dependency,
    spin_dependency,
)


class TestDataFrameDeps:
    """Test data_frame_deps function"""

    def test_returns_html_dependency(self):
        """Test data_frame_deps returns HTMLDependency"""
        result = data_frame_deps()
        assert isinstance(result, HTMLDependency)

    def test_has_correct_name(self):
        """Test data_frame_deps has correct name"""
        result = data_frame_deps()
        assert result.name == "shiny-data-frame-output"

    def test_uses_shiny_version(self):
        """Test data_frame_deps uses shiny __version__"""
        result = data_frame_deps()
        # version might be a Version object
        assert str(result.version) == __version__


class TestPageOutputDependency:
    """Test page_output_dependency function"""

    def test_returns_html_dependency(self):
        """Test page_output_dependency returns HTMLDependency"""
        result = page_output_dependency()
        assert isinstance(result, HTMLDependency)

    def test_has_correct_name(self):
        """Test page_output_dependency has correct name"""
        result = page_output_dependency()
        assert result.name == "shiny-page-output"

    def test_uses_shiny_version(self):
        """Test page_output_dependency uses shiny __version__"""
        result = page_output_dependency()
        assert str(result.version) == __version__


class TestSpinDependency:
    """Test spin_dependency function"""

    def test_returns_html_dependency(self):
        """Test spin_dependency returns HTMLDependency"""
        result = spin_dependency()
        assert isinstance(result, HTMLDependency)

    def test_has_correct_name(self):
        """Test spin_dependency has correct name"""
        result = spin_dependency()
        assert result.name == "shiny-spin"

    def test_uses_shiny_version(self):
        """Test spin_dependency uses shiny __version__"""
        result = spin_dependency()
        assert str(result.version) == __version__


class TestBusyIndicatorsDep:
    """Test busy_indicators_dep function"""

    def test_returns_html_dependency(self):
        """Test busy_indicators_dep returns HTMLDependency"""
        result = busy_indicators_dep()
        assert isinstance(result, HTMLDependency)

    def test_has_correct_name(self):
        """Test busy_indicators_dep has correct name"""
        result = busy_indicators_dep()
        assert result.name == "shiny-busy-indicators"

    def test_uses_shiny_version(self):
        """Test busy_indicators_dep uses shiny __version__"""
        result = busy_indicators_dep()
        assert str(result.version) == __version__
