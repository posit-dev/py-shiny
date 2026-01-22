"""Tests for shiny._deprecated module."""

import warnings

from shiny._deprecated import ShinyDeprecationWarning, warn_deprecated


class TestWarnDeprecated:
    """Tests for warn_deprecated function."""

    def test_warn_deprecated_basic(self) -> None:
        """Test basic deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warn_deprecated("old_func() is deprecated. Use new_func() instead.")
            assert len(w) == 1
            assert "old_func()" in str(w[0].message)
            assert "deprecated" in str(w[0].message)

    def test_warn_deprecated_message_content(self) -> None:
        """Test deprecation warning message content."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warn_deprecated("Please use the new API.")
            assert len(w) == 1
            assert "new API" in str(w[0].message)

    def test_warn_deprecated_category(self) -> None:
        """Test that deprecation warning has correct category."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warn_deprecated("Test deprecation")
            assert len(w) == 1
            # The warning should be ShinyDeprecationWarning
            assert issubclass(w[0].category, ShinyDeprecationWarning)

    def test_warn_deprecated_with_version(self) -> None:
        """Test deprecation warning with version info."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warn_deprecated("Function deprecated since version 1.0")
            assert len(w) == 1
            assert "version 1.0" in str(w[0].message)

    def test_warn_deprecated_multiple_calls(self) -> None:
        """Test multiple deprecation warnings."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warn_deprecated("First deprecation")
            warn_deprecated("Second deprecation")
            assert len(w) == 2
            assert "First" in str(w[0].message)
            assert "Second" in str(w[1].message)

    def test_warn_deprecated_empty_message(self) -> None:
        """Test deprecation warning with empty message."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warn_deprecated("")
            assert len(w) == 1

    def test_warn_deprecated_special_characters(self) -> None:
        """Test deprecation warning with special characters."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warn_deprecated("Use func(a='value', b=123) instead!")
            assert len(w) == 1
            assert "func(a='value', b=123)" in str(w[0].message)

    def test_warn_deprecated_unicode(self) -> None:
        """Test deprecation warning with unicode characters."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warn_deprecated("Deprecated: use new_function() → better_function()")
            assert len(w) == 1
            assert "→" in str(w[0].message)

    def test_warn_deprecated_multiline(self) -> None:
        """Test deprecation warning with multiline message."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warn_deprecated("Line 1\\nLine 2\\nLine 3")
            assert len(w) == 1
            assert "Line 1" in str(w[0].message)

    def test_warn_deprecated_long_message(self) -> None:
        """Test deprecation warning with a long message."""
        long_message = "This is a very long deprecation message. " * 10
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warn_deprecated(long_message)
            assert len(w) == 1
            assert long_message in str(w[0].message)


class TestShinyDeprecationWarning:
    """Tests for ShinyDeprecationWarning class."""

    def test_is_runtime_warning(self) -> None:
        """Test ShinyDeprecationWarning is a RuntimeWarning."""
        assert issubclass(ShinyDeprecationWarning, RuntimeWarning)

    def test_can_be_raised(self) -> None:
        """Test ShinyDeprecationWarning can be raised as warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warnings.warn("test", ShinyDeprecationWarning, stacklevel=2)
            assert len(w) == 1
            assert w[0].category is ShinyDeprecationWarning
