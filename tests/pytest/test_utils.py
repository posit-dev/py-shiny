import random
import socketserver
from typing import List, Set

import pytest

from shiny._utils import (
    AsyncCallbacks,
    Callbacks,
    drop_none,
    guess_mime_type,
    is_async_callable,
    lists_to_tuples,
    private_seed,
    rand_hex,
    random_port,
    run_coro_sync,
    sort_keys_length,
    wrap_async,
)
from shiny.ui._utils import extract_js_keys, js_eval


class TestDropNone:
    """Tests for the drop_none function."""

    def test_empty_dict(self):
        """Test that empty dict returns empty dict."""
        assert drop_none({}) == {}

    def test_no_none_values(self):
        """Test dict with no None values is returned unchanged."""
        d = {"a": 1, "b": "hello", "c": [1, 2, 3]}
        assert drop_none(d) == d

    def test_all_none_values(self):
        """Test dict with all None values returns empty dict."""
        d = {"a": None, "b": None, "c": None}
        assert drop_none(d) == {}

    def test_mixed_values(self):
        """Test dict with mixed None and non-None values."""
        d = {"a": 1, "b": None, "c": "hello", "d": None}
        assert drop_none(d) == {"a": 1, "c": "hello"}

    def test_preserves_falsy_values(self):
        """Test that falsy values other than None are preserved."""
        d = {"a": 0, "b": "", "c": [], "d": False, "e": None}
        assert drop_none(d) == {"a": 0, "b": "", "c": [], "d": False}


class TestListsToTuples:
    """Tests for the lists_to_tuples function."""

    def test_simple_list(self):
        """Test converting a simple list to tuple."""
        result = lists_to_tuples([1, 2, 3])
        assert result == (1, 2, 3)
        assert isinstance(result, tuple)

    def test_nested_list(self):
        """Test converting nested lists to tuples."""
        result = lists_to_tuples([1, [2, 3], [4, [5, 6]]])
        assert result == (1, (2, 3), (4, (5, 6)))

    def test_dict_with_list_values(self):
        """Test dict with list values gets lists converted."""
        result = lists_to_tuples({"a": [1, 2], "b": [3, 4]})
        assert result == {"a": (1, 2), "b": (3, 4)}

    def test_nested_dict_with_lists(self):
        """Test nested dict with lists gets all lists converted."""
        result = lists_to_tuples({"outer": {"inner": [1, 2, 3]}})
        assert result == {"outer": {"inner": (1, 2, 3)}}

    def test_primitive_values_unchanged(self):
        """Test that primitive values are returned unchanged."""
        assert lists_to_tuples(42) == 42
        assert lists_to_tuples("hello") == "hello"
        assert lists_to_tuples(3.14) == 3.14
        assert lists_to_tuples(True) is True
        assert lists_to_tuples(None) is None

    def test_empty_list(self):
        """Test empty list becomes empty tuple."""
        result = lists_to_tuples([])
        assert result == ()
        assert isinstance(result, tuple)


class TestSortKeysLength:
    """Tests for the sort_keys_length function."""

    def test_ascending_order(self):
        """Test sorting keys by length in ascending order."""
        d = {"abc": 1, "a": 2, "ab": 3}
        result = sort_keys_length(d)
        keys = list(result.keys())
        assert keys == ["a", "ab", "abc"]

    def test_descending_order(self):
        """Test sorting keys by length in descending order."""
        d = {"abc": 1, "a": 2, "ab": 3}
        result = sort_keys_length(d, descending=True)
        keys = list(result.keys())
        assert keys == ["abc", "ab", "a"]

    def test_empty_dict(self):
        """Test empty dict returns empty dict."""
        assert sort_keys_length({}) == {}

    def test_same_length_keys(self):
        """Test keys of same length maintain relative order (stable sort)."""
        d = {"abc": 1, "def": 2, "ghi": 3}
        result = sort_keys_length(d)
        # All keys have same length, original values should be preserved
        assert result == {"abc": 1, "def": 2, "ghi": 3}


class TestGuessMimeType:
    """Tests for the guess_mime_type function."""

    def test_html_file(self):
        """Test HTML file MIME type."""
        assert guess_mime_type("test.html") == "text/html"

    def test_css_file(self):
        """Test CSS file MIME type."""
        assert guess_mime_type("styles.css") == "text/css"

    def test_js_files(self):
        """Test JavaScript file MIME types (including workaround for Windows)."""
        assert guess_mime_type("script.js") == "text/javascript"
        assert guess_mime_type("module.mjs") == "text/javascript"
        assert guess_mime_type("common.cjs") == "text/javascript"

    def test_json_file(self):
        """Test JSON file MIME type."""
        assert guess_mime_type("data.json") == "application/json"

    def test_image_files(self):
        """Test image file MIME types."""
        assert guess_mime_type("image.png") == "image/png"
        assert guess_mime_type("photo.jpg") == "image/jpeg"
        assert guess_mime_type("photo.jpeg") == "image/jpeg"
        assert guess_mime_type("icon.gif") == "image/gif"

    def test_unknown_extension(self):
        """Test unknown extension returns default."""
        assert guess_mime_type("file.xyz123") == "application/octet-stream"

    def test_custom_default(self):
        """Test custom default value."""
        assert guess_mime_type("file.xyz123", default="custom/type") == "custom/type"

    def test_no_extension(self):
        """Test file without extension."""
        # Behavior depends on system, but should return default
        result = guess_mime_type("noextension")
        assert result == "application/octet-stream"


class TestRandHex:
    """Tests for the rand_hex function."""

    def test_correct_length(self):
        """Test that rand_hex returns correct length string."""
        assert len(rand_hex(3)) == 6  # 3 bytes = 6 hex chars
        assert len(rand_hex(8)) == 16  # 8 bytes = 16 hex chars
        assert len(rand_hex(1)) == 2  # 1 byte = 2 hex chars

    def test_valid_hex_chars(self):
        """Test that result contains only valid hex characters."""
        result = rand_hex(16)
        valid_chars = set("0123456789abcdef")
        assert all(c in valid_chars for c in result)

    def test_different_results(self):
        """Test that consecutive calls produce different results."""
        results = {rand_hex(8) for _ in range(100)}
        # With 8 bytes of entropy, collisions should be virtually impossible
        assert len(results) == 100


class TestIsAsyncCallable:
    """Tests for the is_async_callable function."""

    def test_async_function(self):
        """Test detection of async function."""

        async def async_fn():
            return 42

        assert is_async_callable(async_fn) is True

    def test_sync_function(self):
        """Test detection of sync function."""

        def sync_fn():
            return 42

        assert is_async_callable(sync_fn) is False

    def test_async_method_on_class(self):
        """Test detection of async method on callable class."""

        class AsyncCallable:
            async def __call__(self):
                return 42

        obj = AsyncCallable()
        assert is_async_callable(obj) is True

    def test_sync_method_on_class(self):
        """Test detection of sync method on callable class."""

        class SyncCallable:
            def __call__(self):
                return 42

        obj = SyncCallable()
        assert is_async_callable(obj) is False

    def test_lambda(self):
        """Test detection of lambda (sync)."""
        fn = lambda: 42  # noqa: E731
        assert is_async_callable(fn) is False


class TestWrapAsync:
    """Tests for the wrap_async function."""

    @pytest.mark.asyncio
    async def test_wraps_sync_function(self):
        """Test wrapping a sync function makes it awaitable."""

        def sync_fn(x: int) -> int:
            return x * 2

        wrapped = wrap_async(sync_fn)
        result = await wrapped(21)
        assert result == 42

    @pytest.mark.asyncio
    async def test_async_function_unchanged(self):
        """Test that async function is returned unchanged."""

        async def async_fn(x: int) -> int:
            return x * 2

        wrapped = wrap_async(async_fn)
        # Should be the same function object
        assert wrapped is async_fn
        result = await wrapped(21)
        assert result == 42


class TestRunCoroSync:
    """Tests for the run_coro_sync function."""

    def test_sync_coroutine(self):
        """Test running a coroutine that completes synchronously."""

        async def sync_coro():
            return 42

        result = run_coro_sync(sync_coro())
        assert result == 42

    def test_raises_on_non_coroutine(self):
        """Test that non-coroutine raises TypeError."""
        with pytest.raises(TypeError, match="requires a Coroutine object"):
            run_coro_sync(42)  # type: ignore

    def test_raises_on_yielding_coroutine(self):
        """Test that yielding coroutine raises RuntimeError."""
        import asyncio

        async def yielding_coro():
            await asyncio.sleep(0)  # This yields control
            return 42

        with pytest.raises(RuntimeError, match="yielded control"):
            run_coro_sync(yielding_coro())


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
@pytest.mark.flaky(reruns=3)
def test_random_port():

    # Starting port
    port = 9001
    # Test a set of continguous ports
    num_ports = 10
    # Number of times to try to find a port range
    n = 100

    # Make sure a single port can be found
    attempts = 0
    for _ in range(n):
        port_i = port - 1000 + attempts
        attempts += 1
        try:
            assert random_port(port_i, port_i) == port_i
            break
        except RuntimeError as e:
            print(e)
    if attempts == n:
        raise RuntimeError(f"Could not find a usable port in {n} tries")

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
