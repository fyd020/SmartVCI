import typing
from enum import Enum
import pytest
from jidutest_can import CanController
from jidutest_can.resource import CanSdbSystem


def get_item_by_option_or_ini(name: str, pytestconfig: pytest.Config):
    all_can_config = eval(pytestconfig.getini("can"))
    can_sdb_system = CanSdbSystem()
    ini_value = all_can_config.get(name)
    ini_value = can_sdb_system.get_sdb_file_path(ini_value) if name.endswith("_path") else ini_value
    return ini_value


class CanCtrlConfig(object):

    def __init__(self,
                 name: typing.Union[str, None]=None,
                 interface: typing.Union[str, None]=None,
                 channel: typing.Union[str, None]=None,
                 db_path: typing.Union[str, None]=None) -> None:

        self.__name = name
        self.__interface = interface
        self.__channel = channel
        self.__db_path = db_path

    @property
    def name(self) -> typing.Union[str, None]:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        self.__name = value

    @property
    def interface(self) -> typing.Union[str, None]:
        return self.__interface

    @interface.setter
    def interface(self, value: str) -> None:
        self.__interface = value

    @property
    def channel(self) -> typing.Union[str, None]:
        return self.__channel

    @channel.setter
    def channel(self, value: str) -> None:
        self.__channel = value

    @property
    def db_path(self) -> typing.Union[str, None]:
        return self.__db_path

    @db_path.setter
    def db_path(self, value: str) -> None:
        self.__db_path = value

    def __repr__(self) -> str:
        return f"CanBusConfig(" + \
               f"name={self.name}, " + \
               f"interface={self.interface}, " + \
               f"channel={self.channel}, " + \
               f"db_path={self.db_path})"

    def add_dict_config(self, dict_config: dict) -> None:
        self.name = dict_config.get("name")
        self.interface = dict_config.get("interface")
        self.channel = dict_config.get("channel")
        self.db_path = dict_config.get("db_path")


@pytest.fixture(scope="session")
def ad_can_config(pytestconfig: pytest.Config) -> typing.Union[CanCtrlConfig, None]:
    if not get_item_by_option_or_ini("ad_can", pytestconfig):
        return None

    dict_config = {
        "name": get_item_by_option_or_ini("ad_can_name", pytestconfig),
        "interface": get_item_by_option_or_ini("ad_can_interface", pytestconfig),
        "channel": get_item_by_option_or_ini("ad_can_channel", pytestconfig),
        "db_path": get_item_by_option_or_ini("ad_can_db_path", pytestconfig),
    }
    config = CanCtrlConfig()
    config.add_dict_config(dict_config)
    return config


@pytest.fixture(scope="session")
def ad_private1_can_config(pytestconfig: pytest.Config) -> typing.Union[CanCtrlConfig, None]:
    if not get_item_by_option_or_ini("ad_private1_can", pytestconfig):
        return None

    dict_config = {
        "name": get_item_by_option_or_ini("ad_private1_can_name", pytestconfig),
        "interface": get_item_by_option_or_ini("ad_private1_can_interface", pytestconfig),
        "channel": get_item_by_option_or_ini("ad_private1_can_channel", pytestconfig),
        "db_path": get_item_by_option_or_ini("ad_private1_can_db_path", pytestconfig),
    }
    config = CanCtrlConfig()
    config.add_dict_config(dict_config)
    return config


@pytest.fixture(scope="session")
def ad_private2_can_config(pytestconfig: pytest.Config) -> typing.Union[CanCtrlConfig, None]:
    if not get_item_by_option_or_ini("ad_private2_can", pytestconfig):
        return None

    dict_config = {
        "name": get_item_by_option_or_ini("ad_private2_can_name", pytestconfig),
        "interface": get_item_by_option_or_ini("ad_private2_can_interface", pytestconfig),
        "channel": get_item_by_option_or_ini("ad_private2_can_channel", pytestconfig),
        "db_path": get_item_by_option_or_ini("ad_private2_can_db_path", pytestconfig),
    }
    config = CanCtrlConfig()
    config.add_dict_config(dict_config)
    return config


@pytest.fixture(scope="session")
def ad_redundancy_can_config(pytestconfig: pytest.Config) -> typing.Union[CanCtrlConfig, None]:
    if not get_item_by_option_or_ini("ad_redundancy_can", pytestconfig):
        return None

    dict_config = {
        "name": get_item_by_option_or_ini("ad_redundancy_can_name", pytestconfig),
        "interface": get_item_by_option_or_ini("ad_redundancy_can_interface", pytestconfig),
        "channel": get_item_by_option_or_ini("ad_redundancy_can_channel", pytestconfig),
        "db_path": get_item_by_option_or_ini("ad_redundancy_can_db_path", pytestconfig),
    }
    config = CanCtrlConfig()
    config.add_dict_config(dict_config)
    return config


@pytest.fixture(scope="session")
def body_can_config(pytestconfig: pytest.Config) -> typing.Union[CanCtrlConfig, None]:
    if not get_item_by_option_or_ini("body_can", pytestconfig):
        return None

    dict_config = {
        "name": get_item_by_option_or_ini("body_can_name", pytestconfig),
        "interface": get_item_by_option_or_ini("body_can_interface", pytestconfig),
        "channel": get_item_by_option_or_ini("body_can_channel", pytestconfig),
        "db_path": get_item_by_option_or_ini("body_can_db_path", pytestconfig),
    }
    config = CanCtrlConfig()
    config.add_dict_config(dict_config)
    return config


@pytest.fixture(scope="session")
def body_alm1_can_config(pytestconfig: pytest.Config) -> typing.Union[CanCtrlConfig, None]:
    if not get_item_by_option_or_ini("body_alm1_can", pytestconfig):
        return None

    dict_config = {
        "name": get_item_by_option_or_ini("body_alm1_can_name", pytestconfig),
        "interface": get_item_by_option_or_ini("body_alm1_can_interface", pytestconfig),
        "channel": get_item_by_option_or_ini("body_alm1_can_channel", pytestconfig),
        "db_path": get_item_by_option_or_ini("body_alm1_can_db_path", pytestconfig),
    }
    config = CanCtrlConfig()
    config.add_dict_config(dict_config)
    return config


@pytest.fixture(scope="session")
def body_alm2_can_config(pytestconfig: pytest.Config) -> typing.Union[CanCtrlConfig, None]:
    if not get_item_by_option_or_ini("body_alm2_can", pytestconfig):
        return None

    dict_config = {
        "name": get_item_by_option_or_ini("body_alm2_can_name", pytestconfig),
        "interface": get_item_by_option_or_ini("body_alm2_can_interface", pytestconfig),
        "channel": get_item_by_option_or_ini("body_alm2_can_channel", pytestconfig),
        "db_path": get_item_by_option_or_ini("body_alm2_can_db_path", pytestconfig),
    }
    config = CanCtrlConfig()
    config.add_dict_config(dict_config)
    return config


@pytest.fixture(scope="session")
def body_exposed_can_config(pytestconfig: pytest.Config) -> typing.Union[CanCtrlConfig, None]:
    if not get_item_by_option_or_ini("body_exposed_can", pytestconfig):
        return None

    dict_config = {
        "name": get_item_by_option_or_ini("body_exposed_can_name", pytestconfig),
        "interface": get_item_by_option_or_ini("body_exposed_can_interface", pytestconfig),
        "channel": get_item_by_option_or_ini("body_exposed_can_channel", pytestconfig),
        "db_path": get_item_by_option_or_ini("body_exposed_can_db_path", pytestconfig),
    }
    config = CanCtrlConfig()
    config.add_dict_config(dict_config)
    return config


@pytest.fixture(scope="session")
def info_can_config(pytestconfig: pytest.Config) -> typing.Union[CanCtrlConfig, None]:
    if not get_item_by_option_or_ini("info_can", pytestconfig):
        return None

    dict_config = {
        "name": get_item_by_option_or_ini("info_can_name", pytestconfig),
        "interface": get_item_by_option_or_ini("info_can_interface", pytestconfig),
        "channel": get_item_by_option_or_ini("info_can_channel", pytestconfig),
        "db_path": get_item_by_option_or_ini("info_can_db_path", pytestconfig),
    }
    config = CanCtrlConfig()
    config.add_dict_config(dict_config)
    return config


@pytest.fixture(scope="session")
def info_private_can_config(pytestconfig: pytest.Config) -> typing.Union[CanCtrlConfig, None]:
    if not get_item_by_option_or_ini("info_private_can", pytestconfig):
        return None

    dict_config = {
        "name": get_item_by_option_or_ini("info_private_can_name", pytestconfig),
        "interface": get_item_by_option_or_ini("info_private_can_interface", pytestconfig),
        "channel": get_item_by_option_or_ini("info_private_can_channel", pytestconfig),
        "db_path": get_item_by_option_or_ini("info_private_can_db_path", pytestconfig),
    }
    config = CanCtrlConfig()
    config.add_dict_config(dict_config)
    return config


@pytest.fixture(scope="session")
def chassis1_can_config(pytestconfig: pytest.Config) -> typing.Union[CanCtrlConfig, None]:
    if not get_item_by_option_or_ini("chassis1_can", pytestconfig):
        return None

    dict_config = {
        "name": get_item_by_option_or_ini("chassis1_can_name", pytestconfig),
        "interface": get_item_by_option_or_ini("chassis1_can_interface", pytestconfig),
        "channel": get_item_by_option_or_ini("chassis1_can_channel", pytestconfig),
        "db_path": get_item_by_option_or_ini("chassis1_can_db_path", pytestconfig),
    }
    config = CanCtrlConfig()
    config.add_dict_config(dict_config)
    return config


@pytest.fixture(scope="session")
def chassis2_can_config(pytestconfig: pytest.Config) -> typing.Union[CanCtrlConfig, None]:
    if not get_item_by_option_or_ini("chassis2_can", pytestconfig):
        return None

    dict_config = {
        "name": get_item_by_option_or_ini("chassis2_can_name", pytestconfig),
        "interface": get_item_by_option_or_ini("chassis2_can_interface", pytestconfig),
        "channel": get_item_by_option_or_ini("chassis2_can_channel", pytestconfig),
        "db_path": get_item_by_option_or_ini("chassis2_can_db_path", pytestconfig),
    }
    config = CanCtrlConfig()
    config.add_dict_config(dict_config)
    return config


@pytest.fixture(scope="session")
def connectivity_can_config(pytestconfig: pytest.Config) -> typing.Union[CanCtrlConfig, None]:
    if not get_item_by_option_or_ini("connectivity_can", pytestconfig):
        return None

    dict_config = {
        "name": get_item_by_option_or_ini("connectivity_can_name", pytestconfig),
        "interface": get_item_by_option_or_ini("connectivity_can_interface", pytestconfig),
        "channel": get_item_by_option_or_ini("connectivity_can_channel", pytestconfig),
        "db_path": get_item_by_option_or_ini("connectivity_can_db_path", pytestconfig),
    }
    config = CanCtrlConfig()
    config.add_dict_config(dict_config)
    return config


@pytest.fixture(scope="session")
def diagnostic_can_config(pytestconfig: pytest.Config) -> typing.Union[CanCtrlConfig, None]:
    if not get_item_by_option_or_ini("diagnostic_can", pytestconfig):
        return None

    dict_config = {
        "name": get_item_by_option_or_ini("diagnostic_can_name", pytestconfig),
        "interface": get_item_by_option_or_ini("diagnostic_can_interface", pytestconfig),
        "channel": get_item_by_option_or_ini("diagnostic_can_channel", pytestconfig),
        "db_path": get_item_by_option_or_ini("diagnostic_can_db_path", pytestconfig),
    }
    config = CanCtrlConfig()
    config.add_dict_config(dict_config)
    return config


@pytest.fixture(scope="session")
def flr_can_config(pytestconfig: pytest.Config) -> typing.Union[CanCtrlConfig, None]:
    if not get_item_by_option_or_ini("flr_can", pytestconfig):
        return None

    dict_config = {
        "name": get_item_by_option_or_ini("flr_can_name", pytestconfig),
        "interface": get_item_by_option_or_ini("flr_can_interface", pytestconfig),
        "channel": get_item_by_option_or_ini("flr_can_channel", pytestconfig),
        "db_path": get_item_by_option_or_ini("flr_can_db_path", pytestconfig),
    }
    config = CanCtrlConfig()
    config.add_dict_config(dict_config)
    return config


@pytest.fixture(scope="session")
def propulsion_can_config(pytestconfig: pytest.Config) -> typing.Union[CanCtrlConfig, None]:
    if not get_item_by_option_or_ini("propulsion_can", pytestconfig):
        return None

    dict_config = {
        "name": get_item_by_option_or_ini("propulsion_can_name", pytestconfig),
        "interface": get_item_by_option_or_ini("propulsion_can_interface", pytestconfig),
        "channel": get_item_by_option_or_ini("propulsion_can_channel", pytestconfig),
        "db_path": get_item_by_option_or_ini("propulsion_can_db_path", pytestconfig),
    }
    config = CanCtrlConfig()
    config.add_dict_config(dict_config)
    return config


@pytest.fixture(scope="session")
def passive_safety_can_config(pytestconfig: pytest.Config) -> typing.Union[CanCtrlConfig, None]:
    if not get_item_by_option_or_ini("passive_safety_can", pytestconfig):
        return None

    dict_config = {
        "name": get_item_by_option_or_ini("passive_safety_can_name", pytestconfig),
        "interface": get_item_by_option_or_ini("passive_safety_can_interface", pytestconfig),
        "channel": get_item_by_option_or_ini("passive_safety_can_channel", pytestconfig),
        "db_path": get_item_by_option_or_ini("passive_safety_can_db_path", pytestconfig),
    }
    config = CanCtrlConfig()
    config.add_dict_config(dict_config)
    return config


class CAN_BUS_NAME(Enum):

    AD = "ADCANFD"
    AD_PRIVATE_1 = "ADPrivateCANFD1"
    AD_PRIVATE_2 = "ADPrivateCANFD2"
    AD_REDUNDANCY = "ADRedundancyCAN"
    BODY_ALM_1 = "BodyALMCANFD1"
    BODY_ALM_2 = "BodyALMCANFD2"
    BODY = "BodyCAN"
    BODY_EXPOSED = "BodyExposedCANFD"
    CHASSIS_1 = "ChassisCAN1"
    CHASSIS_2 = "ChassisCAN2"
    CONNECTIVITY = "ConnectivityCANFD"
    DIAGNOSTIC = "DiagnosticCAN"
    INFO = "InfoCANFD"
    INFO_PRIVATE = "PrivateInfoCANFD"
    PASSIVE_SAFETY = "PassiveSafetyCAN"
    PROPULSION = "PropulsionCAN"
    FLR = "FLRCANFD"


@pytest.fixture(scope="session")
def ad_can_controller(ad_can_config: CanCtrlConfig) -> typing.Union[CanController, None]:
    if not ad_can_config:
        return None

    return CanController(
        ad_can_config.name,
        ad_can_config.interface,
        ad_can_config.channel,
        ad_can_config.db_path
    )


@pytest.fixture(scope="session")
def ad_private1_can_controller(ad_private1_can_config: CanCtrlConfig) -> typing.Union[CanController, None]:
    if not ad_private1_can_config:
        return None

    return CanController(
        ad_private1_can_config.name,
        ad_private1_can_config.interface,
        ad_private1_can_config.channel,
        ad_private1_can_config.db_path
    )


@pytest.fixture(scope="session")
def ad_private2_can_controller(ad_private2_can_config: CanCtrlConfig) -> typing.Union[CanController, None]:
    if not ad_private2_can_config:
        return None

    return CanController(
        ad_private2_can_config.name,
        ad_private2_can_config.interface,
        ad_private2_can_config.channel,
        ad_private2_can_config.db_path
    )


@pytest.fixture(scope="session")
def ad_redundancy_can_controller(ad_redundancy_can_config: CanCtrlConfig) -> typing.Union[CanController, None]:
    if not ad_redundancy_can_config:
        return None

    return CanController(
        ad_redundancy_can_config.name,
        ad_redundancy_can_config.interface,
        ad_redundancy_can_config.channel,
        ad_redundancy_can_config.db_path
    )


@pytest.fixture(scope="session")
def body_can_controller(body_can_config: CanCtrlConfig) -> typing.Union[CanController, None]:
    if not body_can_config:
        return None

    return CanController(
        body_can_config.name,
        body_can_config.interface,
        body_can_config.channel,
        body_can_config.db_path
    )


@pytest.fixture(scope="session")
def body_alm1_can_controller(body_alm1_can_config: CanCtrlConfig) -> typing.Union[CanController, None]:
    if not body_alm1_can_config:
        return None

    return CanController(
        body_alm1_can_config.name,
        body_alm1_can_config.interface,
        body_alm1_can_config.channel,
        body_alm1_can_config.db_path
    )


@pytest.fixture(scope="session")
def body_alm2_can_controller(body_alm2_can_config: CanCtrlConfig) -> typing.Union[CanController, None]:
    if not body_alm2_can_config:
        return None

    return CanController(
        body_alm2_can_config.name,
        body_alm2_can_config.interface,
        body_alm2_can_config.channel,
        body_alm2_can_config.db_path
    )


@pytest.fixture(scope="session")
def body_exposed_can_controller(body_exposed_can_config: CanCtrlConfig) -> typing.Union[CanController, None]:
    if not body_exposed_can_config:
        return None

    return CanController(
        body_exposed_can_config.name,
        body_exposed_can_config.interface,
        body_exposed_can_config.channel,
        body_exposed_can_config.db_path
    )


@pytest.fixture(scope="session")
def info_can_controller(info_can_config: CanCtrlConfig) -> typing.Union[CanController, None]:
    if not info_can_config:
        return None

    return CanController(
        info_can_config.name,
        info_can_config.interface,
        info_can_config.channel,
        info_can_config.db_path
    )


@pytest.fixture(scope="session")
def info_private_can_controller(info_private_can_config: CanCtrlConfig) -> typing.Union[CanController, None]:
    if not info_private_can_config:
        return None

    return CanController(
        info_private_can_config.name,
        info_private_can_config.interface,
        info_private_can_config.channel,
        info_private_can_config.db_path
    )


@pytest.fixture(scope="session")
def chassis1_can_controller(chassis1_can_config: CanCtrlConfig) -> typing.Union[CanController, None]:
    if not chassis1_can_config:
        return None

    return CanController(
        chassis1_can_config.name,
        chassis1_can_config.interface,
        chassis1_can_config.channel,
        chassis1_can_config.db_path
    )


@pytest.fixture(scope="session")
def chassis2_can_controller(chassis2_can_config: CanCtrlConfig) -> typing.Union[CanController, None]:
    if not chassis2_can_config:
        return None

    return CanController(
        chassis2_can_config.name,
        chassis2_can_config.interface,
        chassis2_can_config.channel,
        chassis2_can_config.db_path
    )


@pytest.fixture(scope="session")
def connectivity_can_controller(connectivity_can_config: CanCtrlConfig) -> typing.Union[CanController, None]:
    if not connectivity_can_config:
        return None

    return CanController(
        connectivity_can_config.name,
        connectivity_can_config.interface,
        connectivity_can_config.channel,
        connectivity_can_config.db_path
    )


@pytest.fixture(scope="session")
def diagnostic_can_controller(diagnostic_can_config: CanCtrlConfig) -> typing.Union[CanController, None]:
    if not diagnostic_can_config:
        return None

    return CanController(
        diagnostic_can_config.name,
        diagnostic_can_config.interface,
        diagnostic_can_config.channel,
        diagnostic_can_config.db_path
    )


@pytest.fixture(scope="session")
def flr_can_controller(flr_can_config: CanCtrlConfig) -> typing.Union[CanController, None]:
    if not flr_can_config:
        return None

    return CanController(
        flr_can_config.name,
        flr_can_config.interface,
        flr_can_config.channel,
        flr_can_config.db_path
    )


@pytest.fixture(scope="session")
def propulsion_can_controller(propulsion_can_config: CanCtrlConfig) -> typing.Union[CanController, None]:
    if not propulsion_can_config:
        return None

    return CanController(
        propulsion_can_config.name,
        propulsion_can_config.interface,
        propulsion_can_config.channel,
        propulsion_can_config.db_path
    )


@pytest.fixture(scope="session")
def passive_safety_can_controller(passive_safety_can_config: CanCtrlConfig) -> typing.Union[CanController, None]:
    if not passive_safety_can_config:
        return None

    return CanController(
        passive_safety_can_config.name,
        passive_safety_can_config.interface,
        passive_safety_can_config.channel,
        passive_safety_can_config.db_path
    )


@pytest.hookimpl
def pytest_addoption(parser: pytest.Parser):
    group = parser.getgroup("jidutest-can")

    def add_option_ini(option,
                       dest,
                       help="",
                       default="",
                       action="store",
                       option_type=str,
                       ini_type="string",
                       **kwargs):

        if action in ("store_true", "store_false"):
            group.addoption(option,
                            help=help,
                            default=default,
                            action=action,
                            dest=dest,
                            **kwargs)
        else:
            group.addoption(option,
                            help=help,
                            default=default,
                            action=action,
                            dest=dest,
                            type=option_type,
                            **kwargs)

        parser.addini(dest,
                      help=help,
                      type=ini_type,
                      default=default)

    add_option_ini(
        "--can",
        help="Enbale or disable CAN controller",
        default=False,
        action="store",
        dest="can",
        option_type = str,
        ini_type="string"
    )
