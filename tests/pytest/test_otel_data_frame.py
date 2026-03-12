"""
OTel suppression tests for DataFrame internal reactive primitives.

Tests cover:
- The reactive.Value objects inside _init_reactives() have OtelCollectLevel.NONE
- The reactive.effect inside _init_reactives() has OtelCollectLevel.NONE
- All internal primitives are suppressed from OTel tracing
"""

import os
from unittest.mock import Mock, patch

from shiny.otel._collect import OtelCollectLevel

from .otel_helpers import patch_otel_tracing_state


class TestDataFrameInitReactivesSuppressed:
    """Internal primitives in _init_reactives() are suppressed from OTel."""

    def test_internal_values_otel_level_is_none(self):
        """The reactive.Value objects inside _init_reactives have OtelCollectLevel.NONE."""
        from shiny.render._data_frame import data_frame

        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "all"}):
                renderer = data_frame.__new__(data_frame)
                renderer._session = Mock()
                renderer._session.ns = lambda x: x
                renderer._session.id = "test-session"
                renderer._init_reactives()

                # All three internal Values should be suppressed
                assert renderer._value._otel_level == OtelCollectLevel.NONE, (
                    f"Expected NONE but got {renderer._value._otel_level} for _value"
                )
                assert renderer._cell_patch_map._otel_level == OtelCollectLevel.NONE, (
                    f"Expected NONE but got {renderer._cell_patch_map._otel_level} for _cell_patch_map"
                )
                assert renderer._updated_data._otel_level == OtelCollectLevel.NONE, (
                    f"Expected NONE but got {renderer._updated_data._otel_level} for _updated_data"
                )

    def test_internal_effect_otel_level_is_none(self):
        """The cell-style-update effect inside _init_reactives has OtelCollectLevel.NONE."""
        import shiny.reactive._reactives as reactives_mod
        from shiny.render._data_frame import data_frame

        captured_effects: list = []
        original_init = reactives_mod.Effect_.__init__

        def capturing_init(self, fn, *, session=None, **kwargs):
            original_init(self, fn, session=session, **kwargs)
            captured_effects.append(self)

        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "all"}):
                with patch.object(reactives_mod.Effect_, "__init__", capturing_init):
                    renderer = data_frame.__new__(data_frame)
                    renderer._session = Mock()
                    renderer._session.ns = lambda x: x
                    renderer._session.id = "test-session"
                    renderer._init_reactives()

        # At least one Effect_ was created; all internal ones should be NONE
        assert len(captured_effects) >= 1
        for effect in captured_effects:
            assert effect._otel_level == OtelCollectLevel.NONE, (
                f"Expected NONE but got {effect._otel_level} for {effect}"
            )


class TestDataFramePrivateCalcsSuppressed:
    """Private @reactive_calc_method calcs have OtelCollectLevel.NONE."""

    def test_private_nw_data_otel_level_is_none(self):
        from shiny.otel._constants import FUNC_ATTR_OTEL_COLLECT_LEVEL
        from shiny.render._data_frame import data_frame

        fn = data_frame._nw_data
        assert getattr(fn, FUNC_ATTR_OTEL_COLLECT_LEVEL, None) == OtelCollectLevel.NONE

    def test_private_nw_data_patched_otel_level_is_none(self):
        from shiny.otel._constants import FUNC_ATTR_OTEL_COLLECT_LEVEL
        from shiny.render._data_frame import data_frame

        fn = data_frame._nw_data_patched
        assert getattr(fn, FUNC_ATTR_OTEL_COLLECT_LEVEL, None) == OtelCollectLevel.NONE

    def test_private_data_view_all_otel_level_is_none(self):
        from shiny.otel._constants import FUNC_ATTR_OTEL_COLLECT_LEVEL
        from shiny.render._data_frame import data_frame

        fn = data_frame._data_view_all
        assert getattr(fn, FUNC_ATTR_OTEL_COLLECT_LEVEL, None) == OtelCollectLevel.NONE

    def test_private_data_view_selected_otel_level_is_none(self):
        from shiny.otel._constants import FUNC_ATTR_OTEL_COLLECT_LEVEL
        from shiny.render._data_frame import data_frame

        fn = data_frame._data_view_selected
        assert getattr(fn, FUNC_ATTR_OTEL_COLLECT_LEVEL, None) == OtelCollectLevel.NONE

    def test_public_data_otel_level_unset(self):
        """Public .data() has no suppression -- inherits ambient level."""
        from shiny.otel._constants import FUNC_ATTR_OTEL_COLLECT_LEVEL
        from shiny.render._data_frame import data_frame

        fn = data_frame.data
        assert getattr(fn, FUNC_ATTR_OTEL_COLLECT_LEVEL, None) is None

    def test_public_cell_patches_otel_level_unset(self):
        from shiny.otel._constants import FUNC_ATTR_OTEL_COLLECT_LEVEL
        from shiny.render._data_frame import data_frame

        fn = data_frame.cell_patches
        assert getattr(fn, FUNC_ATTR_OTEL_COLLECT_LEVEL, None) is None
