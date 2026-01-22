"""Comprehensive tests for shiny.ui._input_password module."""

from htmltools import Tag


class TestInputPassword:
    """Tests for input_password function."""

    def test_input_password_basic(self):
        """input_password should create a password input."""
        from shiny.ui import input_password

        result = input_password("pwd", "Password")
        assert isinstance(result, Tag)
        assert result.name == "div"
        # Find the input element in children
        input_elem = None
        for child in result.children:
            if hasattr(child, "name") and hasattr(child, "attrs"):
                if getattr(child, "name", None) == "input":  # type: ignore
                    input_elem = child
                    break
        assert input_elem is not None
        assert getattr(input_elem, "attrs", {}).get("type") == "password"  # type: ignore
        assert getattr(input_elem, "attrs", {}).get("id") == "pwd"  # type: ignore

    def test_input_password_with_label(self):
        """input_password should include label."""
        from shiny.ui import input_password

        result = input_password("pwd", "Enter Password")
        html_str = str(result)
        assert "Enter Password" in html_str

    def test_input_password_default_value(self):
        """input_password should have empty default value."""
        from shiny.ui import input_password

        result = input_password("pwd", "Password")
        html_str = str(result)
        assert 'value=""' in html_str

    def test_input_password_with_initial_value(self):
        """input_password should accept initial value."""
        from shiny.ui import input_password

        result = input_password("pwd", "Password", value="secret")
        html_str = str(result)
        assert 'value="secret"' in html_str

    def test_input_password_with_width(self):
        """input_password should accept width parameter."""
        from shiny.ui import input_password

        result = input_password("pwd", "Password", width="300px")
        html_str = str(result)
        assert "300px" in html_str

    def test_input_password_with_placeholder(self):
        """input_password should accept placeholder."""
        from shiny.ui import input_password

        result = input_password("pwd", "Password", placeholder="Enter secret")
        html_str = str(result)
        assert "Enter secret" in html_str

    def test_input_password_update_on_change(self):
        """input_password should have change update mode by default."""
        from shiny.ui import input_password

        result = input_password("pwd", "Password")
        html_str = str(result)
        assert 'data-update-on="change"' in html_str

    def test_input_password_update_on_blur(self):
        """input_password should accept blur update mode."""
        from shiny.ui import input_password

        result = input_password("pwd", "Password", update_on="blur")
        html_str = str(result)
        assert 'data-update-on="blur"' in html_str

    def test_input_password_has_form_control_class(self):
        """input_password should have form-control class."""
        from shiny.ui import input_password

        result = input_password("pwd", "Password")
        html_str = str(result)
        assert "form-control" in html_str

    def test_input_password_has_shiny_input_class(self):
        """input_password should have shiny-input-password class."""
        from shiny.ui import input_password

        result = input_password("pwd", "Password")
        html_str = str(result)
        assert "shiny-input-password" in html_str

    def test_input_password_container_has_form_group(self):
        """input_password container should have form-group class."""
        from shiny.ui import input_password

        result = input_password("pwd", "Password")
        assert "form-group" in result.attrs.get("class", "")
        assert "shiny-input-container" in result.attrs.get("class", "")


class TestModuleExports:
    """Tests for module exports."""

    def test_module_imports_correctly(self):
        """Module should import without errors."""
        import shiny.ui._input_password as input_password_module

        assert input_password_module is not None

    def test_all_exports_exist(self):
        """All items in __all__ should be importable."""
        from shiny.ui import _input_password

        for item in _input_password.__all__:
            assert hasattr(_input_password, item)
