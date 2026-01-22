"""Tests for shiny.reactive._extended_task module"""

import asyncio

import pytest

from shiny.reactive._extended_task import DenialContext, ExtendedTask, Status


class TestExtendedTaskStatus:
    """Test Status type"""

    def test_status_literals(self):
        """Test valid status values"""
        statuses: list[Status] = [
            "initial",
            "running",
            "success",
            "error",
            "cancelled",
        ]
        for status in statuses:
            assert status in ["initial", "running", "success", "error", "cancelled"]


class TestDenialContext:
    """Test DenialContext class"""

    def test_denial_context_creation(self):
        """Test creating a DenialContext"""
        ctx = DenialContext()
        assert ctx is not None

    def test_denial_context_on_invalidate_raises(self):
        """Test on_invalidate raises RuntimeError"""
        ctx = DenialContext()
        with pytest.raises(RuntimeError) as exc_info:
            ctx.on_invalidate(lambda: None)
        assert "reactive sources" in str(exc_info.value).lower()


class TestExtendedTask:
    """Test ExtendedTask class"""

    def test_extended_task_requires_async(self):
        """Test ExtendedTask requires async function"""

        def sync_func():
            return 42

        with pytest.raises(TypeError) as exc_info:
            ExtendedTask(sync_func)  # type: ignore
        assert "async" in str(exc_info.value).lower()

    def test_extended_task_with_async_func(self):
        """Test ExtendedTask accepts async function"""

        async def async_func():
            return 42

        task = ExtendedTask(async_func)
        assert task is not None

    def test_extended_task_initial_status(self):
        """Test ExtendedTask starts with initial status"""

        async def async_func():
            return 42

        task = ExtendedTask(async_func)
        # Status is a reactive Value, we need to access it in isolation
        from shiny.reactive._reactives import isolate

        with isolate():
            assert task.status() == "initial"

    def test_extended_task_has_value(self):
        """Test ExtendedTask has value attribute"""

        async def async_func():
            return 42

        task = ExtendedTask(async_func)
        assert hasattr(task, "value")

    def test_extended_task_has_error(self):
        """Test ExtendedTask has error attribute"""

        async def async_func():
            return 42

        task = ExtendedTask(async_func)
        assert hasattr(task, "error")

    def test_extended_task_callable(self):
        """Test ExtendedTask is callable"""

        async def async_func():
            return 42

        task = ExtendedTask(async_func)
        assert callable(task)

    def test_extended_task_has_invoke(self):
        """Test ExtendedTask has invoke method"""

        async def async_func():
            return 42

        task = ExtendedTask(async_func)
        assert hasattr(task, "invoke")
        assert callable(task.invoke)

    def test_extended_task_has_cancel(self):
        """Test ExtendedTask has cancel method"""

        async def async_func():
            return 42

        task = ExtendedTask(async_func)
        assert hasattr(task, "cancel")
        assert callable(task.cancel)

    def test_extended_task_cancel_clears_queue(self):
        """Test cancel clears invocation queue"""

        async def async_func():
            await asyncio.sleep(0.1)
            return 42

        task = ExtendedTask(async_func)
        # Add something to queue
        task._invocation_queue.append(lambda: None)
        assert len(task._invocation_queue) == 1

        task.cancel()
        assert len(task._invocation_queue) == 0


class TestExtendedTaskDecorator:
    """Test extended_task decorator"""

    def test_import_decorator(self):
        """Test extended_task decorator can be imported"""
        from shiny.reactive._extended_task import extended_task

        assert callable(extended_task)
