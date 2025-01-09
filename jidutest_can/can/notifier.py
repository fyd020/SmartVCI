import sys
import time
import asyncio
import logging
import threading
import typing
import warnings
from queue import Empty
from queue import Queue
from abc import ABCMeta
from abc import abstractmethod
from typing import Any
from typing import Awaitable
from typing import AsyncIterator
from typing import Callable
from typing import Iterable
from typing import Set
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from jidutest_can.can.interfaces import BusABC
from jidutest_can.can.message import RawMessage
from jidutest_can.can.tools import BUS_NOTIFIER_MAPPING


logger = logging.getLogger(__name__)


class Reader(metaclass=ABCMeta):
    """The basic listener that can be called directly to handle some
    CAN message::

        listener = SomeReader()
        msg = my_bus.recv()

        # now either call
        listener(msg)
        # or
        listener.on_message_received(msg)

        # Important to ensure all outputs are flushed
        listener.stop()
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    @abstractmethod
    def on_message_received(self, msg: RawMessage) -> None:
        """This method is called to handle the given message.

        :param msg: the delivered message
        """

    def __call__(self, msg: RawMessage) -> None:
        self.on_message_received(msg)

    def on_error(self, exc: Exception) -> None:
        """This method is called to handle any exception in the receive thread.

        :param exc: The exception causing the thread to stop
        """
        raise NotImplementedError()

    def stop(self) -> None:
        """
        Stop handling new messages, carry out any final tasks to ensure
        data is persisted and cleanup any open resources.

        Concrete implementations override.
        """


class RedirectReader(Reader):  # pylint: disable=abstract-method
    """
    A RedirectReader sends all received messages to another Bus.
    """

    def __init__(self, bus: BusABC, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.bus = bus

    def on_message_received(self, msg: RawMessage) -> None:
        self.bus.send(msg)


class BufferedReader(Reader):  # pylint: disable=abstract-method
    """
    A BufferedReader is a subclass of :class:`~can.Reader` which implements a
    **message buffer**: that is, when the :class:`can.BufferedReader` instance is
    notified of a new message it pushes it into a queue of messages waiting to
    be serviced. The messages can then be fetched with
    :meth:`~can.BufferedReader.get_message`.

    Putting in messages after :meth:`~can.BufferedReader.stop` has been called will raise
    an exception, see :meth:`~can.BufferedReader.on_message_received`.

    :attr is_stopped: ``True`` if the reader has been stopped
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        # set to "infinite" size
        self.buffer: Queue[RawMessage] = Queue()
        self.is_stopped: bool = False

    def on_message_received(self, msg: RawMessage) -> None:
        """Append a message to the buffer.

        :raises: BufferError
            if the reader has already been stopped
        """
        if self.is_stopped:
            raise RuntimeError("reader has already been stopped")
        else:
            self.buffer.put(msg)

    def get_message(self, timeout: float = 0.5) -> Optional[RawMessage]:
        """
        Attempts to retrieve the message that has been in the queue for the longest amount
        of time (FIFO). If no message is available, it blocks for given timeout or until a
        message is received (whichever is shorter), or else returns None. This method does
        not block after :meth:`can.BufferedReader.stop` has been called.

        :param timeout: The number of seconds to wait for a new message.
        :return: the received :class:`can.RawMessage` or `None`, if the queue is empty.
        """
        try:
            if self.is_stopped:
                return self.buffer.get(block=False)
            else:
                return self.buffer.get(block=True, timeout=timeout)
        except Empty:
            return None

    def stop(self) -> None:
        """Prohibits any more additions to this reader."""
        self.is_stopped = True


class AsyncBufferedReader(Reader):  # pylint: disable=abstract-method
    """A message buffer for use with :mod:`asyncio`.

    See :ref:`asyncio` for how to use with :class:`can.Notifier`.

    Can also be used as an asynchronous iterator::

        async for msg in reader:
            print(msg)
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.buffer: "asyncio.Queue[RawMessage]"

        if "loop" in kwargs:
            warnings.warn(
                "The 'loop' argument is deprecated since python-can 4.0.0 "
                "and has no effect starting with Python 3.10",
                DeprecationWarning,
            )
            if sys.version_info < (3, 10):
                self.buffer = asyncio.Queue(loop=kwargs["loop"])
                return

        self.buffer = asyncio.Queue()

    def on_message_received(self, msg: RawMessage) -> None:
        """Append a message to the buffer.

        Must only be called inside an event loop!
        """
        self.buffer.put_nowait(msg)

    async def get_message(self) -> RawMessage:
        """
        Retrieve the latest message when awaited for::

            msg = await reader.get_message()

        :return: The CAN message.
        """
        return await self.buffer.get()

    def __aiter__(self) -> AsyncIterator[RawMessage]:
        return self

    def __anext__(self) -> Awaitable[RawMessage]:
        return self.buffer.get()


MessageRecipient = Union[Reader, Callable[[RawMessage], Union[Awaitable[None], None]]]


class Notifier:
    
    def __init__(
        self,
        bus: Union[BusABC, List[BusABC], typing.Tuple[BusABC], Set[BusABC]],
        listeners: Iterable[MessageRecipient],
        timeout: float = 1.0,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        """Manages the distribution of :class:`~can.RawMessage` instances to listeners.

        Supports multiple buses and listeners.

        .. Note::

            Remember to call `stop()` after all messages are received as
            many listeners carry out flush operations to persist data.


        :param bus: A :ref:`bus` or a list of buses to listen to.
        :param listeners:
            An iterable of :class:`~can.Reader` or callables that receive a :class:`~can.RawMessage`
            and return nothing.
        :param timeout: An optional maximum number of seconds to wait for any :class:`~can.RawMessage`.
        :param loop: An :mod:`asyncio` event loop to schedule the ``listeners`` in.
        """
        self.listeners: Set[MessageRecipient] = set(listeners)
        self.timeout = timeout
        self._loop = loop

        #: Exception raised in thread
        self.exceptions: Optional[Dict[bus, Exception]] = dict()

        self._running = True
        self._lock = threading.Lock()

        self._readers: Dict[Union[BusABC, List[BusABC]], Union[int, threading.Thread]] = dict()
        self.buses = set(bus if isinstance(bus, (list, tuple, set)) else [bus])
        for each_bus in self.buses:
            self.add_bus(each_bus)
        for listener in self.listeners.copy():
            self.add_listener(listener)

    def add_bus(self, bus: BusABC) -> None:
        """Add a bus for notification.

        :param bus:
            CAN bus instance.
        """
        self.buses.add(bus)
        thread_name = f'can.notifier.recv for bus "{bus.channel_info}"'
        for _thread in threading.enumerate():
            if thread_name == _thread.name and bus not in self.exceptions:
                logger.warning(f"There are already {thread_name} thread recving,"
                               f"do not start the {bus.channel_info} recv thread.")
                # 增加如下判断的目的：防止多个notifier对象中管理的不同bus同时往一个blf/asc文件中写数据时有问题
                notifier: Notifier = BUS_NOTIFIER_MAPPING.get(bus)
                if notifier:
                    notifier._lock = self._lock
                return
        BUS_NOTIFIER_MAPPING[bus] = self
        reader: int = -1
        try:
            reader = bus.fileno()
        except NotImplementedError:
            # CanBus doesn't support fileno, we fall back to thread based reader
            pass

        if self._loop is not None and reader >= 0:
            # Use bus file descriptor to watch for messages
            self._loop.add_reader(reader, self._on_message_available, bus)
            self._readers[bus] = reader
        else:
            reader_thread = threading.Thread(
                target=self._rx_thread,
                args=(bus,),
                name=thread_name,
            )
            reader_thread.daemon = True
            reader_thread.start()
            self._readers[bus] = reader_thread

    def stop(self, timeout: float = 5) -> None:
        """Stop notifying Readers when new :class:`~can.RawMessage` objects arrive
        and call :meth:`~can.Reader.stop` on each Reader.

        :param timeout:
            Max time in seconds to wait for receive threads to finish.
            Should be longer than timeout given at instantiation.
        """
        self._running = False
        end_time = time.time() + timeout
        for reader in self._readers.values():
            if isinstance(reader, threading.Thread):
                now = time.time()
                if now < end_time:
                    reader.join(end_time - now)
            elif self._loop:
                # reader is a file descriptor
                self._loop.remove_reader(reader)
        for listener in self.listeners.copy():
            # Mypy prefers this over a hasattr(...) check
            getattr(listener, "stop", lambda: None)()

    def _rx_thread(self, bus: BusABC) -> None:
        msg = None
        try:
            while self._running:
                if msg is not None:
                    with self._lock:
                        if self._loop is not None:
                            self._loop.call_soon_threadsafe(
                                self._on_message_received, msg
                            )
                        else:
                            self._on_message_received(msg)
                msg = bus.recv(self.timeout)
                # logger.info(f"Notifier recv msg: {msg}")
        except Exception as exc:  # pylint: disable=broad-except
            self.exceptions[bus] = exc
            logger.exception(exc)
            if self._loop is not None:
                self._loop.call_soon_threadsafe(self._on_error, exc)
                # Raise anyways
                raise
            elif not self._on_error(exc):
                # If it was not handled, raise the exception here
                raise
            else:
                # It was handled, so only log it
                logger.info("suppressed exception: %s", exc)

    def _on_message_available(self, bus: BusABC) -> None:
        msg = bus.recv(0)
        if msg is not None:
            self._on_message_received(msg)

    def _on_message_received(self, msg: RawMessage) -> None:
        for callback in self.listeners.copy():
            res = callback(msg)
            if res is not None and self._loop is not None and asyncio.iscoroutine(res):
                # Schedule coroutine
                self._loop.create_task(res)

    def _on_error(self, exc: Exception) -> bool:
        """Calls ``on_error()`` for all listeners if they implement it.

        :returns: ``True`` if at least one error handler was called.
        """
        was_handled = False

        for listener in self.listeners.copy():
            on_error = getattr(
                listener, "on_error", None
            )  # Mypy prefers this over hasattr(...)
            if on_error is not None:
                try:
                    on_error(exc)
                except NotImplementedError:
                    pass
                else:
                    was_handled = True

        return was_handled

    def add_listener(self, listener: MessageRecipient) -> None:
        """Add new Reader to the notification list.
        If it is already present, it will be called two times
        each time a message arrives.

        :param listener: Reader to be added to the list to be notified
        """
        buses_without_reader = self.buses - self._readers.keys()
        for bus in buses_without_reader:
            BUS_NOTIFIER_MAPPING[bus].add_listener(listener)
        self.listeners.add(listener)

    def remove_listener(self, listener: MessageRecipient) -> None:
        """Remove a listener from the notification list. This method
        throws an exception if the given listener is not part of the
        stored listeners.

        :param listener: Reader to be removed from the list to be notified
        :raises ValueError: if `listener` was never added to this notifier
        """
        buses_without_reader = self.buses - self._readers.keys()
        for bus in buses_without_reader:
            BUS_NOTIFIER_MAPPING[bus].remove_listener(listener)
        if isinstance(listener, BufferedReader):
            listener.buffer.queue.clear()
        if listener in self.listeners:
            self.listeners.remove(listener)
