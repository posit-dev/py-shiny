import pytest
from shiny.utils import AsyncCallbacks, Callbacks


def test_callbacks():
    class MockCallback:
        def __init__(self):
            self.exec_count = 0

        def __call__(self):
            self.exec_count += 1

    callbacks = Callbacks()

    cb1 = MockCallback()
    cb2 = MockCallback()
    cb3 = MockCallback()
    cb4 = MockCallback()

    def mutate_registrations():
        # Unregister cb2
        cb2_reg_handle()
        # Calling registrations multiple times should just no-op
        cb2_reg_handle()

        callbacks.register(cb4)

    _ = callbacks.register(cb1)
    mut_reg_handle = callbacks.register(mutate_registrations)
    cb2_reg_handle = callbacks.register(cb2)
    _ = callbacks.register(cb3, once=True)

    callbacks.invoke()
    assert cb1.exec_count == 1  # Regular registration was called
    assert cb2.exec_count == 1  # Unregistered by an earlier handler, but still called
    assert cb3.exec_count == 1  # once=True registration was called
    assert cb4.exec_count == 0  # Registered during invoke(), not called

    mut_reg_handle()

    callbacks.invoke()
    assert cb1.exec_count == 2  # Regular registration was called again
    assert cb2.exec_count == 1  # Unregistered by previous invoke, not called again
    assert cb3.exec_count == 1  # once=True, so not called again
    assert cb4.exec_count == 1  # Registered during previous invoke(), was called


@pytest.mark.asyncio
async def test_async_callbacks():
    class AsyncMockCallback:
        def __init__(self):
            self.exec_count = 0

        async def __call__(self):
            self.exec_count += 1

    callbacks = AsyncCallbacks()

    cb1 = AsyncMockCallback()
    cb2 = AsyncMockCallback()
    cb3 = AsyncMockCallback()
    cb4 = AsyncMockCallback()

    async def mutate_registrations():
        # Unregister cb2
        cb2_reg_handle()
        # Calling registrations multiple times should just no-op
        cb2_reg_handle()

        callbacks.register(cb4)

    _ = callbacks.register(cb1)
    mut_reg_handle = callbacks.register(mutate_registrations)
    cb2_reg_handle = callbacks.register(cb2)
    _ = callbacks.register(cb3, once=True)

    await callbacks.invoke()
    assert cb1.exec_count == 1  # Regular registration was called
    assert cb2.exec_count == 1  # Unregistered by an earlier handler, but still called
    assert cb3.exec_count == 1  # once=True registration was called
    assert cb4.exec_count == 0  # Registered during invoke(), not called

    mut_reg_handle()

    await callbacks.invoke()
    assert cb1.exec_count == 2  # Regular registration was called again
    assert cb2.exec_count == 1  # Unregistered by previous invoke, not called again
    assert cb3.exec_count == 1  # once=True, so not called again
    assert cb4.exec_count == 1  # Registered during previous invoke(), was called
