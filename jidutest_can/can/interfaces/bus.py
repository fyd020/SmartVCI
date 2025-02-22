"""
Contains the ABC bus implementation and its documentation.
"""

import contextlib
import logging
import queue
import threading
from time import time
from enum import auto
from enum import Enum
from abc import ABC
from abc import ABCMeta
from abc import abstractmethod
from typing import Any
from typing import cast
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple
from typing import Sequence
from typing import Union
from jidutest_can.can.tools import AutoDetectedConfig
from jidutest_can.can.tools import CanFilters
from jidutest_can.can.tools import CanFilterExtended
from jidutest_can.can.bcm import CyclicSendTaskABC
from jidutest_can.can.bcm import ThreadBasedCyclicSendTask
from jidutest_can.can.bcm import ThreadBasedReceiveTask
from jidutest_can.can.message import RawMessage


logger = logging.getLogger("jidutest_can.can")
log_autodetect = logger.getChild("detect_available_configs")


class BusState(Enum):
    """The state in which a :class:`can.BusABC` can be."""

    ACTIVE = auto()
    PASSIVE = auto()
    ERROR = auto()


class BusABC(metaclass=ABCMeta):
    """The CAN Bus Abstract Base Class that serves as the basis
    for all concrete interfaces.

    This class may be used as an iterator over the received messages
    and as a context manager for auto-closing the bus when done using it.

    Please refer to :ref:`errors` for possible exceptions that may be
    thrown by certain operations on this bus.
    """

    #: a string describing the underlying bus and/or channel
    channel_info = "unknown"

    #: Log level for received messages
    RECV_LOGGING_LEVEL = 9

    _is_shutdown: bool = False

    @abstractmethod
    def __init__(
        self,
        channel: Any,
        can_filters: Optional[CanFilters] = None,
        **kwargs: object,
    ):
        """Construct and open a CAN bus instance of the specified type.

        Subclasses should call though this method with all given parameters
        as it handles generic tasks like applying filters.

        :param channel:
            The can interface identifier. Expected type is backend dependent.

        :param can_filters:
            See :meth:`~can.BusABC.set_filters` for details.

        :param dict kwargs:
            Any backend dependent configurations are passed in this dictionary

        :raises ValueError: If parameters are out of range
        :raises ~can.exceptions.CanInterfaceNotImplementedError:
            If the driver cannot be accessed
        :raises ~can.exceptions.CanInitializationError:
            If the bus cannot be initialized
        """
        self._periodic_tasks: List[Union[_SelfRemovingCyclicTask, ThreadBasedCyclicSendTask]] = []
        self._cylic_task = None
        self.set_filters(can_filters)

    def __str__(self) -> str:
        return self.channel_info

    def recv(self, timeout: Optional[float] = None) -> Optional[RawMessage]:
        """Block waiting for a message from the Bus.

        :param timeout:
            seconds to wait for a message or None to wait indefinitely

        :return:
            :obj:`None` on timeout or a :class:`~can.RawMessage` object.

        :raises ~can.exceptions.CanOperationError:
            If an error occurred while reading
        """
        start = time()
        time_left = timeout

        while True:
            # try to get a message
            msg, already_filtered = self._recv_internal(timeout=time_left)

            # return it, if it matches
            if msg and (already_filtered or self._matches_filters(msg)):
                logger.log(self.RECV_LOGGING_LEVEL, "Received: %s", msg)
                return msg

            # if not, and timeout is None, try indefinitely
            elif timeout is None:
                continue

            # try next one only if there still is time, and with
            # reduced timeout
            else:
                time_left = timeout - (time() - start)

                if time_left > 0:
                    continue

                return None

    def _recv_internal(
        self, timeout: Optional[float]
    ) -> Tuple[Optional[RawMessage], bool]:
        """
        Read a message from the bus and tell whether it was filtered.
        This methods may be called by :meth:`~can.BusABC.recv`
        to read a message multiple times if the filters set by
        :meth:`~can.BusABC.set_filters` do not match and the call has
        not yet timed out.

        New implementations should always override this method instead of
        :meth:`~can.BusABC.recv`, to be able to take advantage of the
        software based filtering provided by :meth:`~can.BusABC.recv`
        as a fallback. This method should never be called directly.

        .. note::

            This method is not an `@abstractmethod` (for now) to allow older
            external implementations to continue using their existing
            :meth:`~can.BusABC.recv` implementation.

        .. note::

            The second return value (whether filtering was already done) may
            change over time for some interfaces, like for example in the
            Kvaser interface. Thus it cannot be simplified to a constant value.

        :param float timeout: seconds to wait for a message,
                              see :meth:`~can.BusABC.send`

        :return:
            1.  a message that was read or None on timeout
            2.  a bool that is True if message filtering has already
                been done and else False

        :raises ~can.exceptions.CanOperationError:
            If an error occurred while reading
        :raises NotImplementedError:
            if the bus provides it's own :meth:`~can.BusABC.recv`
            implementation (legacy implementation)

        """
        raise NotImplementedError("Trying to read from a write only bus?")

    def recv_cyclic(
        self, 
        q: queue.Queue, 
        timeout: Optional[float] = None,
        duration: Optional[float] = None,
        ) -> ThreadBasedReceiveTask:
        
        logger.info("Start receiving messages")
        self._cylic_task = ThreadBasedReceiveTask(self, q, timeout, duration)
        return self._cylic_task

    @abstractmethod
    def send(self, msg: RawMessage, timeout: Optional[float] = None) -> None:
        """Transmit a message to the CAN bus.

        Override this method to enable the transmit path.

        :param RawMessage msg: A message object.

        :param timeout:
            If > 0, wait up to this many seconds for message to be ACK'ed or
            for transmit queue to be ready depending on driver implementation.
            If timeout is exceeded, an exception will be raised.
            Might not be supported by all interfaces.
            None blocks indefinitely.

        :raises ~can.exceptions.CanOperationError:
            If an error occurred while sending
        """
        raise NotImplementedError("Trying to write to a readonly bus?")

    def send_periodic(
        self,
        msgs: Union[RawMessage, Sequence[RawMessage]],
        period: float,
        duration: Optional[float] = None,
        store_task: bool = True,
    ) -> CyclicSendTaskABC:
        """Start sending messages at a given period on this bus.

        The task will be active until one of the following conditions are met:

        - the (optional) duration expires
        - the Bus instance goes out of scope
        - the Bus instance is shutdown
        - :meth:`stop_all_periodic_tasks` is called
        - the task's :meth:`~can.broadcastmanager.CyclicTask.stop` method is called.

        :param msgs:
            RawMessage(s) to transmit
        :param period:
            Period in seconds between each message
        :param duration:
            Approximate duration in seconds to continue sending messages. If
            no duration is provided, the task will continue indefinitely.
        :param store_task:
            If True (the default) the task will be attached to this Bus instance.
            Disable to instead manage tasks manually.
        :return:
            A started task instance. Note the task can be stopped (and depending on
            the backend modified) by calling the task's
            :meth:`~can.broadcastmanager.CyclicTask.stop` method.

        .. note::

            Note the duration before the messages stop being sent may not
            be exactly the same as the duration specified by the user. In
            general the message will be sent at the given rate until at
            least **duration** seconds.

        .. note::

            For extremely long running Bus instances with many short lived
            tasks the default api with ``store_task==True`` may not be
            appropriate as the stopped tasks are still taking up memory as they
            are associated with the Bus instance.
        """
        if isinstance(msgs, RawMessage):
            msgs = [msgs]
        elif isinstance(msgs, Sequence):
            # A Sequence does not necessarily provide __bool__ we need to use len()
            if len(msgs) == 0:
                raise ValueError("Must be a sequence at least of length 1")
        else:
            raise ValueError("Must be either a message or a sequence of messages")

        # Create a backend specific task; will be patched to a _SelfRemovingCyclicTask later
        task = cast(
            _SelfRemovingCyclicTask,
            self._send_periodic_internal(msgs, period, duration),
        )

        # we wrap the task's stop method to also remove it from the Bus's list of tasks
        periodic_tasks = self._periodic_tasks
        original_stop_method = task.stop

        def wrapped_stop_method(remove_task: bool = True) -> None:
            nonlocal task, periodic_tasks, original_stop_method
            if remove_task:
                try:
                    periodic_tasks.remove(task)
                except ValueError:
                    pass  # allow the task to be already removed
            original_stop_method()

        task.stop = wrapped_stop_method  # type: ignore

        if store_task:
            self._periodic_tasks.append(task)

        return task

    def _send_periodic_internal(
        self,
        msgs: Union[Sequence[RawMessage], RawMessage],
        period: float,
        duration: Optional[float] = None,
    ) -> CyclicSendTaskABC:
        """Default implementation of periodic message sending using threading.

        Override this method to enable a more efficient backend specific approach.

        :param msgs:
            RawMessages to transmit
        :param period:
            Period in seconds between each message
        :param duration:
            The duration between sending each message at the given rate. If
            no duration is provided, the task will continue indefinitely.
        :return:
            A started task instance. Note the task can be stopped (and
            depending on the backend modified) by calling the
            :meth:`~can.broadcastmanager.CyclicTask.stop` method.
        """
        if not hasattr(self, "_lock_send_periodic"):
            # Create a send lock for this bus, but not for buses which override this method
            self._lock_send_periodic = (  # pylint: disable=attribute-defined-outside-init
                threading.Lock()
            )
        task = ThreadBasedCyclicSendTask(
            self, self._lock_send_periodic, msgs, period, duration
        )
        return task

    def stop_all_periodic_tasks(self, remove_tasks: bool = True) -> None:
        """Stop sending any messages that were started using :meth:`send_periodic`.

        .. note::
            The result is undefined if a single task throws an exception while being stopped.

        :param remove_tasks:
            Stop tracking the stopped tasks.
        """
        if not hasattr(self, "_periodic_tasks"):
            # avoid AttributeError for partially initialized BusABC instance
            return

        for task in self._periodic_tasks:
            # we cannot let `task.stop()` modify `self._periodic_tasks` while we are
            # iterating over it (#634)
            task.stop(remove_task=False)

        if remove_tasks:
            self._periodic_tasks.clear()

    def stop_cyclic_task(self) -> None:
        self._cylic_task.stop() 
        
    def __iter__(self) -> Iterator[RawMessage]:
        """Allow iteration on messages as they are received.

        .. code-block:: python

            for msg in bus:
                print(msg)


        :yields:
            :class:`RawMessage` msg objects.
        """
        while True:
            msg = self.recv(timeout=1.0)
            if msg is not None:
                yield msg

    @property
    def filters(self) -> Optional[CanFilters]:
        """
        Modify the filters of this bus. See :meth:`~can.BusABC.set_filters`
        for details.
        """
        return self._filters

    @filters.setter
    def filters(self, filters: Optional[CanFilters]) -> None:
        self.set_filters(filters)

    def set_filters(
        self, filters: Optional[CanFilters] = None
    ) -> None:
        """Apply filtering to all messages received by this Bus.

        All messages that match at least one filter are returned.
        If `filters` is `None` or a zero length sequence, all
        messages are matched.

        Calling without passing any filters will reset the applied
        filters to ``None``.

        :param filters:
            A iterable of dictionaries each containing a "can_id",
            a "can_mask", and an optional "extended" key::

                [{"can_id": 0x11, "can_mask": 0x21, "extended": False}]

            A filter matches, when
            ``<received_can_id> & can_mask == can_id & can_mask``.
            If ``extended`` is set as well, it only matches messages where
            ``<received_is_extended> == extended``. Else it matches every
            messages based only on the arbitration ID and mask.
        """
        self._filters = filters or None
        self._apply_filters(self._filters)

    def _apply_filters(self, filters: Optional[CanFilters]) -> None:
        """
        Hook for applying the filters to the underlying kernel or
        hardware if supported/implemented by the interface.

        :param filters:
            See :meth:`~can.BusABC.set_filters` for details.
        """

    def _matches_filters(self, msg: RawMessage) -> bool:
        """Checks whether the given message matches at least one of the
        current filters. See :meth:`~can.BusABC.set_filters` for details
        on how the filters work.

        This method should not be overridden.

        :param msg:
            the message to check if matching
        :return: whether the given message matches at least one filter
        """

        # if no filters are set, all messages are matched
        if self._filters is None:
            return True
        if msg.arbitration_id == 1 and msg.dlc == 4 and msg.data == bytes([0, 0, 0, 0]):
            return False

        for _filter in self._filters:
            # check if this filter even applies to the message
            if "extended" in _filter:
                _filter = cast(CanFilterExtended, _filter)
                if _filter["extended"] != msg.is_extended_id:
                    continue

            # then check for the mask and id
            can_id = _filter["can_id"]
            can_mask = _filter["can_mask"]

            # basically, we compute
            # `msg.arbitration_id & can_mask == can_id & can_mask`
            # by using the shorter, but equivalent from below:
            if (can_id ^ msg.arbitration_id) & can_mask == 0:
                return True

        # nothing matched
        return False

    def flush_tx_buffer(self) -> None:
        """Discard every message that may be queued in the output buffer(s)."""

    def shutdown(self) -> None:
        """
        Called to carry out any interface specific cleanup required in shutting down a bus.

        This method can be safely called multiple times.
        """
        if self._is_shutdown:
            logger.debug("%s is already shut down", self.__class__)
            return

        self._is_shutdown = True
        self.stop_all_periodic_tasks()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    def __del__(self) -> None:
        if not self._is_shutdown:
            logger.warning("%s was not properly shut down", self.__class__.__name__)
            # We do some best-effort cleanup if the user
            # forgot to properly close the bus instance
            with contextlib.suppress(AttributeError):
                self.shutdown()

    @property
    def state(self) -> BusState:
        """
        Return the current state of the hardware
        """
        return BusState.ACTIVE

    @state.setter
    def state(self, new_state: BusState) -> None:
        """
        Set the new state of the hardware
        """
        raise NotImplementedError("Property is not implemented.")

    @staticmethod
    def _detect_available_configs() -> List[AutoDetectedConfig]:
        """Detect all configurations/channels that this interface could
        currently connect with.

        This might be quite time consuming.

        May not to be implemented by every interface on every platform.

        :return: an iterable of dicts, each being a configuration suitable
                 for usage in the interface's bus constructor.
        """
        raise NotImplementedError()

    def fileno(self) -> int:
        raise NotImplementedError("fileno is not implemented using current CAN bus")

    @property
    def periodic_tasks(self):
        return self._periodic_tasks


class _SelfRemovingCyclicTask(CyclicSendTaskABC, ABC):
    """Removes itself from a bus.

    Only needed for typing :meth:`CanBus._periodic_tasks`. Do not instantiate.
    """

    def stop(self, remove_task: bool = True) -> None:
        raise NotImplementedError()
