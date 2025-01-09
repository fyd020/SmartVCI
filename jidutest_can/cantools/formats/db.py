from typing import List
from typing import Optional

from jidutest_can.cantools.database import BusConfig
from jidutest_can.cantools.database import Message
from jidutest_can.cantools.database import Node
from jidutest_can.cantools.formats.dbc_specifics import DbcSpecifics
from jidutest_can.cantools.formats.arxml import AutosarDatabaseSpecifics


class InternalDatabase(object):
    """Internal CAN database.

    """

    def __init__(self,
                 messages: List[Message],
                 nodes: List[Node],
                 buses: List[BusConfig],
                 version : Optional[str],
                 dbc_specifics: Optional[DbcSpecifics] = None,
                 autosar_specifics: Optional[AutosarDatabaseSpecifics] = None):
        self.messages = messages
        self.nodes = nodes
        self.buses = buses
        self.version = version
        self.dbc = dbc_specifics
        self.autosar = autosar_specifics
