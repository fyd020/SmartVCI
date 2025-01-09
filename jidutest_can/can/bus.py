import logging
import importlib
from threading import RLock
from typing import Any
from typing import cast
from typing import Iterable
from typing import List
from typing import Optional
from typing import Type
from typing import Union
from jidutest_can.can.interfaces import BACKENDS
from jidutest_can.can.interfaces import BusABC
from jidutest_can.can.tools import AutoDetectedConfig
from jidutest_can.can.tools import CanInterfaceNotImplementedError
from jidutest_can.can.tools import Channel
from jidutest_can.can.util import load_config


logger = logging.getLogger("jidutest_can.can")
log_autodetect = logger.getChild("detect_available_configs")


### python-can/interface.py ###
def _get_class_for_interface(interface: str) -> Type[BusABC]:
    """
    Returns the main bus class for the given interface.

    :raises:
        NotImplementedError if the interface is not known
    :raises CanInterfaceNotImplementedError:
         if there was a problem while importing the interface or the bus class within that
    """
    # Find the correct backend
    try:
        module_name, class_name = BACKENDS[interface]
    except KeyError:
        raise NotImplementedError(
            f"CAN interface '{interface}' not supported"
        ) from None

    # Import the correct interface module
    try:
        module = importlib.import_module(module_name)
    except Exception as e:
        raise CanInterfaceNotImplementedError(
            f"Cannot import module {module_name} for CAN interface '{interface}': {e}"
        ) from None

    # Get the correct class
    try:
        bus_class = getattr(module, class_name)
    except Exception as e:
        raise CanInterfaceNotImplementedError(
            f"Cannot import class {class_name} from module {module_name} for CAN interface "
            f"'{interface}': {e}"
        ) from None

    return cast(Type[BusABC], bus_class)


class CanBus(BusABC):  # pylint: disable=abstract-method
    """Bus wrapper with configuration loading.

    Instantiates a CAN Bus of the given ``interface``, falls back to reading a
    configuration file from default locations.

    :param channel:
        Channel identification. Expected type is backend dependent.
        Set to ``None`` to let it be resolved automatically from the default
        :ref:`configuration`.

    :param interface:
        See :ref:`interface names` for a list of supported interfaces.
        Set to ``None`` to let it be resolved automatically from the default
        :ref:`configuration`.

    :param args:
        ``interface`` specific positional arguments.

    :param kwargs:
        ``interface`` specific keyword arguments.

    :raises ~can.exceptions.CanInterfaceNotImplementedError:
        if the ``interface`` isn't recognized or cannot be loaded

    :raises ~can.exceptions.CanInitializationError:
        if the bus cannot be instantiated

    :raises ValueError:
        if the ``channel`` could not be determined
    """

    @staticmethod
    def __new__(  # type: ignore  # pylint: disable=keyword-arg-before-vararg
        cls: Any,
        channel: Optional[Channel] = None,
        interface: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> BusABC:
        # figure out the rest of the configuration; this might raise an error
        if interface is not None:
            kwargs["interface"] = interface
        if channel is not None:
            kwargs["channel"] = channel
        if "context" in kwargs:
            context = kwargs["context"]
            del kwargs["context"]
        else:
            context = None
        kwargs = load_config(config=kwargs, context=context)

        # resolve the bus class to use for that interface
        cls = _get_class_for_interface(kwargs["interface"])

        # remove the "interface" key, so it doesn't get passed to the backend
        del kwargs["interface"]

        # make sure the bus can handle this config format
        if "channel" not in kwargs:
            raise ValueError("'channel' argument missing")
        else:
            channel = kwargs["channel"]
            del kwargs["channel"]

        if channel is None:
            # Use the default channel for the backend
            bus = cls(*args, **kwargs)
        else:
            bus = cls(channel, *args, **kwargs)

        return cast(BusABC, bus)


def detect_available_configs(
    interfaces: Union[None, str, Iterable[str]] = None
) -> List[AutoDetectedConfig]:
    """Detect all configurations/channels that the interfaces could
    currently connect with.

    This might be quite time consuming.

    Automated configuration detection may not be implemented by
    every interface on every platform. This method will not raise
    an error in that case, but with rather return an empty list
    for that interface.

    :param interfaces: either
        - the name of an interface to be searched in as a string,
        - an iterable of interface names to search in, or
        - `None` to search in all known interfaces.
    :rtype: list[dict]
    :return: an iterable of dicts, each suitable for usage in
             the constructor of :class:`can.BusABC`.
    """

    # Figure out where to search
    if interfaces is None:
        interfaces = BACKENDS
    elif isinstance(interfaces, str):
        interfaces = (interfaces,)
    # else it is supposed to be an iterable of strings

    result = []
    for interface in interfaces:

        try:
            bus_class = _get_class_for_interface(interface)
        except CanInterfaceNotImplementedError:
            log_autodetect.debug(
                'interface "%s" cannot be loaded for detection of available configurations',
                interface,
            )
            continue

        # get available channels
        try:
            available = list(
                bus_class._detect_available_configs()  # pylint: disable=protected-access
            )
        except NotImplementedError:
            log_autodetect.debug(
                'interface "%s" does not support detection of available configurations',
                interface,
            )
        else:
            log_autodetect.debug(
                'interface "%s" detected %i available configurations',
                interface,
                len(available),
            )

            # add the interface name to the configs if it is not already present
            for config in available:
                if "interface" not in config:
                    config["interface"] = interface

            # append to result
            result += available

    return result



### python-can/thread_safe_bus.py ###
try:
    from wrapt import ObjectProxy
    import_exc = None
except ImportError as exc:
    ObjectProxy = object
    import_exc = exc

try:
    from contextlib import nullcontext
except ImportError:
    class nullcontext:  # type: ignore
        """A context manager that does nothing at all.
        A fallback for Python 3.7's :class:`contextlib.nullcontext` manager.
        """

        def __init__(self, enter_result=None):
            self.enter_result = enter_result

        def __enter__(self):
            return self.enter_result

        def __exit__(self, *args):
            pass


class ThreadSafeBus(ObjectProxy):  # pylint: disable=abstract-method
    """
    Contains a thread safe :class:`can.BusABC` implementation that
    wraps around an existing interface instance. All public methods
    of that base class are now safe to be called from multiple threads.
    The send and receive methods are synchronized separately.

    Use this as a drop-in replacement for :class:`~can.BusABC`.

    .. note::

        This approach assumes that both :meth:`~can.BusABC.send` and
        :meth:`~can.BusABC._recv_internal` of the underlying bus instance can be
        called simultaneously, and that the methods use :meth:`~can.BusABC._recv_internal`
        instead of :meth:`~can.BusABC.recv` directly.
    """

    def __init__(self, *args, **kwargs):
        if import_exc is not None:
            raise import_exc

        super().__init__(CanBus(*args, **kwargs))

        # now, BusABC.send_periodic() does not need a lock anymore, but the
        # implementation still requires a context manager
        # pylint: disable=protected-access
        self.__wrapped__._lock_send_periodic = nullcontext()
        # pylint: enable=protected-access

        # init locks for sending and receiving separately
        self._lock_send = RLock()
        self._lock_recv = RLock()

    def recv(
        self, timeout=None, *args, **kwargs
    ):  # pylint: disable=keyword-arg-before-vararg
        with self._lock_recv:
            return self.__wrapped__.recv(timeout=timeout, *args, **kwargs)

    def send(
        self, msg, timeout=None, *args, **kwargs
    ):  # pylint: disable=keyword-arg-before-vararg
        with self._lock_send:
            return self.__wrapped__.send(msg, timeout=timeout, *args, **kwargs)

    # send_periodic does not need a lock, since the underlying
    # `send` method is already synchronized

    @property
    def filters(self):
        with self._lock_recv:
            return self.__wrapped__.filters

    @filters.setter
    def filters(self, filters):
        with self._lock_recv:
            self.__wrapped__.filters = filters

    def set_filters(
        self, filters=None, *args, **kwargs
    ):  # pylint: disable=keyword-arg-before-vararg
        with self._lock_recv:
            return self.__wrapped__.set_filters(filters=filters, *args, **kwargs)

    def flush_tx_buffer(self, *args, **kwargs):
        with self._lock_send:
            return self.__wrapped__.flush_tx_buffer(*args, **kwargs)

    def shutdown(self, *args, **kwargs):
        with self._lock_send, self._lock_recv:
            return self.__wrapped__.shutdown(*args, **kwargs)

    @property
    def state(self):
        with self._lock_send, self._lock_recv:
            return self.__wrapped__.state

    @state.setter
    def state(self, new_state):
        with self._lock_send, self._lock_recv:
            self.__wrapped__.state = new_state
