"""Tests for shiny/render/transformer/__init__.py - Transformer module exports."""

from shiny.render import transformer


class TestTransformerExports:
    """Tests for transformer module exports."""

    def test_transformermetadata_exported(self):
        """Test TransformerMetadata is exported."""
        assert hasattr(transformer, "TransformerMetadata")

    def test_transformerparams_exported(self):
        """Test TransformerParams is exported."""
        assert hasattr(transformer, "TransformerParams")

    def test_outputrenderer_exported(self):
        """Test OutputRenderer is exported."""
        assert hasattr(transformer, "OutputRenderer")

    def test_output_transformer_exported(self):
        """Test output_transformer is exported."""
        assert hasattr(transformer, "output_transformer")
        assert callable(transformer.output_transformer)

    def test_is_async_callable_exported(self):
        """Test is_async_callable is exported."""
        assert hasattr(transformer, "is_async_callable")
        assert callable(transformer.is_async_callable)

    def test_valuefn_exported(self):
        """Test ValueFn is exported."""
        assert hasattr(transformer, "ValueFn")


class TestTransformerAll:
    """Tests for __all__ exports."""

    def test_all_is_tuple(self):
        """Test __all__ is a tuple."""
        assert isinstance(transformer.__all__, tuple)

    def test_all_contains_transformermetadata(self):
        """Test __all__ contains TransformerMetadata."""
        assert "TransformerMetadata" in transformer.__all__

    def test_all_contains_transformerparams(self):
        """Test __all__ contains TransformerParams."""
        assert "TransformerParams" in transformer.__all__

    def test_all_contains_outputrenderer(self):
        """Test __all__ contains OutputRenderer."""
        assert "OutputRenderer" in transformer.__all__

    def test_all_contains_output_transformer(self):
        """Test __all__ contains output_transformer."""
        assert "output_transformer" in transformer.__all__

    def test_all_contains_is_async_callable(self):
        """Test __all__ contains is_async_callable."""
        assert "is_async_callable" in transformer.__all__

    def test_all_contains_valuefn(self):
        """Test __all__ contains ValueFn."""
        assert "ValueFn" in transformer.__all__


class TestIsAsyncCallable:
    """Tests for is_async_callable function."""

    def test_sync_function_returns_false(self):
        """Test sync function returns False."""

        def sync_fn():
            return 1

        assert transformer.is_async_callable(sync_fn) is False

    def test_async_function_returns_true(self):
        """Test async function returns True."""

        async def async_fn():
            return 1

        assert transformer.is_async_callable(async_fn) is True

    def test_lambda_returns_false(self):
        """Test lambda returns False."""
        assert transformer.is_async_callable(lambda: 1) is False
