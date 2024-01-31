import random
import socketserver
from typing import List, Set

import pytest

from shiny._utils import AsyncCallbacks, Callbacks, private_seed, random_port
from shiny.ui._utils import extract_js_keys, js_eval


def test_randomness():
    current_state = random.getstate()
    try:
        # Make sure the public stream of randomness is independent of the private stream
        # https://github.com/posit-dev/py-shiny/issues/140
        pub = random.randint(0, 100000000)
        with private_seed():
            priv = random.randint(0, 100000000)
        pub2 = random.randint(0, 100000000)
        with private_seed():
            priv2 = random.randint(0, 100000000)
        assert pub != priv and priv != pub2 and pub2 != priv2

        # By setting the same seed, we should get the same randomness
        random.seed(0)
        public = [random.randint(0, 100000000) for _ in range(3)]
        with private_seed():
            random.seed(0)
            private = [random.randint(0, 100000000) for _ in range(3)]
        assert public == private

        # Interleaved calls to private and public should give the same randomness
        public: List[float] = []
        private: List[float] = []
        random.seed(0)
        with private_seed():
            random.seed(0)
        public.append(random.randint(0, 100000000))
        with private_seed():
            private.append(random.randint(0, 100000000))
        with private_seed():
            private.append(random.randint(0, 100000000))
        public.append(random.randint(0, 100000000))
        public.append(random.randint(0, 100000000))
        with private_seed():
            private.append(random.randint(0, 100000000))
        assert public == private

    finally:
        random.setstate(current_state)


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


# Timeout within 2 seconds
@pytest.mark.timeout(2)
@pytest.mark.flaky(reruns=3, reruns_delay=1)
def test_random_port():
    assert random_port(9000, 9000) == 9000

    # Starting port
    port = 9001
    # Test a set of continguous ports
    num_ports = 10
    # Number of times to try to find a port range
    n = 100

    # Find a range of `num_ports` ports that are all available
    attempts = 0
    for _ in range(n):
        attempts += 1
        j = 0
        try:
            for j in range(num_ports):
                random_port(port + j, port + j)
            # If we reach this point, we have found a plausible range of ports to use
            break

        except RuntimeError as e:
            print(e)
            # Port `port + j` is busy,
            # Shift the test range and try again
            port += j + 1
            print("Trying port: ", port)
    # If no port is available, throw an error
    # `attempts` should be << n
    if attempts == n:
        raise RuntimeError(
            f"Could not find {num_ports} continguous ports to use for testing in {n} tries"
        )

    seen: Set[int] = set()
    # Ensure that `num_ports` unique random ports are eventually generated. If not (e.g. if the
    # max port number is treated as exclusive instead of inclusive, say) then the while
    # loop will not exit and the test will timeout.
    max_port = port + num_ports - 1
    while len(seen) < num_ports:
        seen.add(random_port(port, max_port))

    assert len(seen) == num_ports


def test_random_port_unusable():
    # 6000 is an unsafe port, make sure that it fails
    with pytest.raises(RuntimeError, match="Failed to find a usable random port"):
        random_port(6000, 6000)


def test_random_port_starvation():
    port = 9000
    for _ in range(100):
        try:
            with socketserver.TCPServer(
                ("127.0.0.1", port),
                socketserver.BaseRequestHandler,
            ):
                with pytest.raises(
                    RuntimeError, match="Failed to find a usable random port"
                ):
                    random_port(port, port)
        except OSError as e:
            print(e)
            # Port is busy, bump the port number
            port += 1
            print("Trying port: ", port)


def test_extract_js_keys():
    options = {
        "key1": "value1",
        "key2": js_eval("<h1>Hello, world!</h1>"),
        "key3": {
            "subkey1": js_eval("console.log('Hello, world!');"),
            "subkey2": "value2",
            "subkey3": {
                "subsubkey1": js_eval("<p>This is a paragraph.</p>"),
                "subsubkey2": "value3",
            },
        },
        "key4": "value4",
    }

    assert extract_js_keys(options) == [
        "key2",
        "key3.subkey1",
        "key3.subkey3.subsubkey1",
    ]
