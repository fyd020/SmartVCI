import abc
import queue
import sys
import time
import logging
import threading
from typing import Callable
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import TYPE_CHECKING
from typing import Union
from typing_extensions import Final

from jidutest_can.can.tools import CanOperationError
from jidutest_can.can.tools import BUS_NOTIFIER_MAPPING
from jidutest_can.can.tools import Channel
from jidutest_can.can.message import RawMessage

if TYPE_CHECKING:
    from jidutest_can.can.interfaces import BusABC


# try to import win32event for event-based cyclic send task (needs the pywin32 package)
USE_WINDOWS_EVENTS = False
try:
    import win32event

    # Python 3.11 provides a more precise sleep implementation on Windows, so this is not necessary.
    # Put version check here, so mypy does not complain about `win32event` not being defined.
    if sys.version_info < (3, 11):
        USE_WINDOWS_EVENTS = True
except ImportError:
    pass


logger = logging.getLogger(__name__)
NANOSECONDS_IN_SECOND: Final[int] = 1_000_000_000
NANOSECONDS_IN_MILLISECOND: Final[int] = 1_000_000


class CyclicTask(abc.ABC):
    """
    Abstract Base for all cyclic tasks.
    """

    @abc.abstractmethod
    def stop(self) -> None:
        """Cancel this periodic task.

        :raises ~can.exceptions.CanError:
            If stop is called on an already stopped task.
        """


class CyclicSendTaskABC(CyclicTask):
    """
    RawMessage send task with defined period
    """

    def __init__(
        self, messages: Union[Sequence[RawMessage], RawMessage], period: float
    ) -> None:
        """
        :param messages:
            The messages to be sent periodically.
        :param period: The rate in seconds at which to send the messages.

        :raises ValueError: If the given messages are invalid
        """
        messages = self._check_and_convert_messages(messages)

        # Take the Arbitration ID of the first element
        self.arbitration_id = messages[0].arbitration_id
        self.period = period
        self.period_ns = int(round(period * 1e9))
        self.messages = messages

    @staticmethod
    def _check_and_convert_messages(
        messages: Union[Sequence[RawMessage], RawMessage]
    ) -> Tuple[RawMessage, ...]:
        """Helper function to convert a RawMessage or Sequence of messages into a
        tuple, and raises an error when the given value is invalid.

        Performs error checking to ensure that all Messages have the same
        arbitration ID and channel.

        Should be called when the cyclic task is initialized.

        :raises ValueError: If the given messages are invalid
        """
        if not isinstance(messages, (list, tuple)):
            if isinstance(messages, RawMessage):
                messages = [messages]
            else:
                raise ValueError("Must be either a list, tuple, or a RawMessage")
        if not messages:
            raise ValueError("Must be at least a list or tuple of length 1")
        messages = tuple(messages)

        all_same_id = all(
            message.arbitration_id == messages[0].arbitration_id for message in messages
        )
        if not all_same_id:
            raise ValueError("All Arbitration IDs should be the same")

        all_same_channel = all(
            message.channel == messages[0].channel for message in messages
        )
        if not all_same_channel:
            raise ValueError("All Channel IDs should be the same")

        return messages


class LimitedDurationCyclicSendTaskABC(CyclicSendTaskABC):
    
    def __init__(
        self,
        messages: Union[Sequence[RawMessage], RawMessage],
        period: float,
        duration: Optional[float],
    ) -> None:
        """RawMessage send task with a defined duration and period.

        :param messages:
            The messages to be sent periodically.
        :param period: The rate in seconds at which to send the messages.
        :param duration:
            Approximate duration in seconds to continue sending messages. If
            no duration is provided, the task will continue indefinitely.

        :raises ValueError: If the given messages are invalid
        """
        super().__init__(messages, period)
        self.duration = duration


class RestartableCyclicTaskABC(CyclicSendTaskABC):
    """Adds support for restarting a stopped cyclic task"""

    @abc.abstractmethod
    def start(self) -> None:
        """Restart a stopped periodic task."""


class ModifiableCyclicTaskABC(CyclicSendTaskABC):
    """Adds support for modifying a periodic message"""

    def _check_modified_messages(self, messages: Tuple[RawMessage, ...]) -> None:
        """Helper function to perform error checking when modifying the data in
        the cyclic task.

        Performs error checking to ensure the arbitration ID and the number of
        cyclic messages hasn't changed.

        Should be called when modify_data is called in the cyclic task.

        :raises ValueError: If the given messages are invalid
        """
        if len(self.messages) != len(messages):
            raise ValueError(
                "The number of new cyclic messages to be sent must be equal to "
                "the number of messages originally specified for this task"
            )
        if self.arbitration_id != messages[0].arbitration_id:
            raise ValueError(
                "The arbitration ID of new cyclic messages cannot be changed "
                "from when the task was created"
            )

    def modify_data(self, messages: Union[Sequence[RawMessage], RawMessage]) -> None:
        """Update the contents of the periodically sent messages, without
        altering the timing.

        :param messages:
            The messages with the new :attr:`RawMessage.data`.

            Note: The arbitration ID cannot be changed.

            Note: The number of new cyclic messages to be sent must be equal
            to the original number of messages originally specified for this
            task.

        :raises ValueError: If the given messages are invalid
        """
        messages = self._check_and_convert_messages(messages)
        self._check_modified_messages(messages)

        self.messages = messages


class MultiRateCyclicSendTaskABC(CyclicSendTaskABC):
    """A Cyclic send task that supports switches send frequency after a set time."""

    def __init__(
        self,
        channel: Channel,
        messages: Union[Sequence[RawMessage], RawMessage],
        count: int,  # pylint: disable=unused-argument
        initial_period: float,  # pylint: disable=unused-argument
        subsequent_period: float,
    ) -> None:
        """
        Transmits a message `count` times at `initial_period` then continues to
        transmit messages at `subsequent_period`.

        :param channel: See interface specific documentation.
        :param messages:
        :param count:
        :param initial_period:
        :param subsequent_period:

        :raises ValueError: If the given messages are invalid
        """
        super().__init__(messages, subsequent_period)
        self._channel = channel


class ThreadBasedCyclicSendTask(
    ModifiableCyclicTaskABC, LimitedDurationCyclicSendTaskABC, RestartableCyclicTaskABC
):
    """Fallback cyclic send task using daemon thread."""

    def __init__(
        self,
        bus: "BusABC",
        lock: threading.Lock,
        messages: Union[Sequence[RawMessage], RawMessage],
        period: float,
        duration: Optional[float] = None,
        on_error: Optional[Callable[[Exception], bool]] = None,
    ) -> None:
        """Transmits `messages` with a `period` seconds for `duration` seconds on a `bus`.

        The `on_error` is called if any error happens on `bus` while sending `messages`.
        If `on_error` present, and returns ``False`` when invoked, thread is
        stopped immediately, otherwise, thread continuously tries to send `messages`
        ignoring errors on a `bus`. Absence of `on_error` means that thread exits immediately
        on error.

        :param on_error: The callable that accepts an exception if any
                         error happened on a `bus` while sending `messages`,
                         it shall return either ``True`` or ``False`` depending
                         on desired behaviour of `ThreadBasedCyclicSendTask`.

        :raises ValueError: If the given messages are invalid
        """
        super().__init__(messages, period, duration)
        self.bus = bus
        self.send_lock = lock
        self.stopped = True
        self.thread: Optional[threading.Thread] = None
        self.end_time: Optional[float] = (
            time.perf_counter() + duration if duration else None
        )
        self.on_error = on_error
        self.exception: Optional[Exception] = None
        if USE_WINDOWS_EVENTS:
            self.period_ms = int(round(period * 1000, 0))
            try:
                self.event = win32event.CreateWaitableTimerEx(
                    None,
                    None,
                    win32event.CREATE_WAITABLE_TIMER_HIGH_RESOLUTION,
                    win32event.TIMER_ALL_ACCESS,
                )
            except (AttributeError, OSError):
                self.event = win32event.CreateWaitableTimer(None, False, None)

        self.start()

    def stop(self) -> None:
        if USE_WINDOWS_EVENTS:
            win32event.CancelWaitableTimer(self.event.handle)
        self.stopped = True

    def start(self) -> None:
        self.stopped = False
        if self.thread is None or not self.thread.is_alive():
            name = f"Cyclic send task for 0x{self.messages[0].arbitration_id:X}"
            self.thread = threading.Thread(target=self._run, name=name)
            self.thread.daemon = True

            if USE_WINDOWS_EVENTS:
                win32event.SetWaitableTimer(
                    self.event.handle, 0, self.period_ms, None, None, False
                )

            self.thread.start()

    def _run(self) -> None:
        msg_index = 0
        msg_due_time_ns = time.perf_counter_ns()

        while not self.stopped:
            # Prevent calling bus.send from multiple threads
            message = self.messages[msg_index]
            message.timestamp = time.time()
            with self.send_lock:
                try:
                    self.bus.send(message)
                except Exception as exc:  # pylint: disable=broad-except
                    self.exception = exc
                    logger.exception(f"{threading.currentThread().name}:{exc}")
                    if self.on_error:
                        if not self.on_error(exc):
                            break
                    else:
                        break
            notifier = BUS_NOTIFIER_MAPPING.get(self.bus)
            if notifier and not self.bus.channel_info.startswith("TOSUN_CANBUS"):
                getattr(notifier, "_on_message_received")(message)
            msg_due_time_ns += self.period_ns
            if self.end_time is not None and time.perf_counter() >= self.end_time:
                break
            msg_index = (msg_index + 1) % len(self.messages)

            # Compensate for the time it takes to send the message
            delay_ns = msg_due_time_ns - time.perf_counter_ns()

            if delay_ns > 0:
                if USE_WINDOWS_EVENTS:
                    win32event.WaitForSingleObject(
                        self.event.handle,
                        int(round(delay_ns / NANOSECONDS_IN_MILLISECOND)),
                    )
                else:
                    time.sleep(delay_ns / NANOSECONDS_IN_SECOND)


class ThreadBasedReceiveTask(CyclicTask):

    def __init__(
            self,
            bus: "BusABC",
            q: queue.Queue,
            timeout: Optional[float] = None,
            duration: Optional[float] = None,
    ) -> None:

        self.__queue = q
        self.__bus = bus
        self.__running = threading.Event()
        self.__running.set()
        self.__timeout = timeout
        self.end_time = (time.perf_counter() + duration if duration else None)
        self.start()

    def _run(self) -> None:
        while self.__running.is_set():
            try:
                raw_message = self.__bus.recv(timeout=self.__timeout)
                if not raw_message:
                    continue
                self.__queue.put(raw_message)
            except CanOperationError:
                logger.warning(f"Receive message failed, please try again")
            else:
                logger.info(f"Receive raw message: {raw_message}")

            if self.end_time is not None and time.perf_counter() >= self.end_time:
                break

    def start(self) -> None:
        thread = threading.Thread(target=self._run, name="Recv_Thread")
        thread.start()

    def stop(self) -> None:
        self.__running.clear()

    def get_dict_list(self) -> queue.Queue:
        return self.__queue
