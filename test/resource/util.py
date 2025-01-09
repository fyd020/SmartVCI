import logging
import os
import stat
import pathlib
import shutil
import typing
from importlib_resources import files
from abc import ABC
from abc import abstractmethod
from jidutest_can.cantools import load_file
from jidutest_can.package import pkg_name


logger = logging.getLogger(__name__)


class SdbSystemABC(ABC):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, pkg_name: str=pkg_name, pkg_res_name: str = "resource") -> None:
        self.__pkg_name = pkg_name
        self.__pkg_res_name = pkg_res_name
        self.__root_path = str(files(f"{self.__pkg_name}.{self.__pkg_res_name}"))

    @property
    def root_path(self):
        return self.__root_path

    def get_sdb_file_path(self,
                          filename: str,
                          sdb_version: typing.Optional[str]=None,
                          ) -> pathlib.Path:
                            
        sdb_path = self.__root_path
        if sdb_version:
            sdb_path = pathlib.Path(self.__root_path, sdb_version)
        file_path = pathlib.Path(sdb_path, filename)
        return file_path

    def get_sdb_folder_path(self,
                            sdb_version: typing.Optional[str]=None,
                            ) -> pathlib.Path:

        sdb_path = self.__root_path
        if sdb_version:
            sdb_path = pathlib.Path(self.__root_path, sdb_version)
        return sdb_path
    
    def read_only_handler(self, func, path, excinfo):
        os.chmod(path, stat.S_IWRITE)
        func(path)
        
    def install_sdb_file(self,
                         source_path: str, 
                         filename: str=None,
                         sdb_version: str=None,
                         tag_name: str=None,
                         username: str=None,
                         password: str=None
                         ) -> None:
        
        remote_path = self.get_remote_sdb_path()
        target_path = self.get_sdb_folder_path(sdb_version)
        sdb_path = pathlib.Path(target_path, "jidusdb")

        if not os.path.exists(target_path):
            os.mkdir(target_path)
        if source_path.startswith(("git@", "http")):
            logger.info("Install from remote side...")
            if os.path.exists(sdb_path):
                userinput = input("Remote SDB file already downloaded, do you want to replace it with a new version? Please input 'y' or 'n':")
                if userinput == "y" or userinput == "yes" or userinput =="Y" or userinput =="YES":              
                    shutil.rmtree(sdb_path, onerror=self.read_only_handler)                   
            if tag_name:
                if source_path.startswith("http") and username and password:
                    os.system(f"cd {target_path} && git clone https://{username}:{password}@{source_path.split('//')[1]} -b {tag_name}")
                else:
                    os.system(f"cd {target_path} && git clone {source_path} -b {tag_name}")
            else:       
                if source_path.startswith("http") and username and password:
                    os.system(f"cd {target_path} && git clone https://{username}:{password}@{source_path.split('//')[1]}") 
                else: 
                    os.system(f"cd {target_path} && git clone {source_path}")                   
            source_path = pathlib.Path(target_path, remote_path)
        else:
            logger.info("Install from local side...")                   
                    
        if os.path.isdir(source_path):
            if filename:
                if self.filter_sdb_file(filename):
                    source_file_path = pathlib.Path(source_path, filename)
                    target_file_path = pathlib.Path(target_path, filename)
                    if os.path.exists(source_file_path):
                        if not os.path.exists(target_file_path):
                            shutil.copyfile(source_file_path, target_file_path)
                            if not self.validate_sdb_file(target_file_path):
                                os.remove(target_file_path)
                            else:
                                logger.info(f"sdb file {filename} installed.")
                        else:
                            logger.info(f"sdb file {filename} already exists.")
                    else:
                        logger.error(f"Error: File not found in local path {source_path}, please check.")
            else:
                for f in os.listdir(source_path):                       
                    if self.filter_sdb_file(f):
                        source_file_path = pathlib.Path(source_path, f)
                        target_file_path = pathlib.Path(target_path, f)
                        if not os.path.exists(target_file_path):
                            shutil.copyfile(source_file_path, target_file_path)
                            if not self.validate_sdb_file(target_file_path):
                                os.remove(target_file_path)
                            else:
                                logger.info(f"sdb file {f} installed.")
                        else:
                            logger.info(f"sdb file {f} already exists.")
                    else:
                        logger.error(f"Error: {f} is not a valid sdb file, please check.")
        else:
            logger.error(f"Error: sdb source files can't be found, please check.")

    def uninstall_sdb_file(self, 
                           filename: str=None,
                           sdb_version: str=None
                           ) -> None:

        target_path = None
        if filename:
            if sdb_version:
                version_path = self.get_sdb_folder_path(sdb_version)
                if os.path.exists(version_path):
                    target_path = self.get_sdb_file_path(filename, sdb_version)
                else:
                    logger.error(f"Error: No folder {version_path}, please check.")
            else:
                target_path = self.get_sdb_file_path(filename, sdb_version)
            if target_path:
                if os.path.exists(target_path):
                    if self.filter_sdb_file(filename):
                        os.remove(target_path)
                        logger.info(f"sdb {filename} uninstalled.")
                    else:
                        logger.error(f"Error: {filename} is not a sdb file, can't uninstall, please check.")
                else:
                    logger.error("Error: No this sdb file, please check.")
        else:
            target_path = self.get_sdb_folder_path(sdb_version)
            if os.path.exists(target_path):
                if sdb_version:
                    shutil.rmtree(target_path, onerror=self.read_only_handler)
                    logger.info(f"sdb version {sdb_version} uninstalled.")
                else:
                    count = 0
                    for f in os.listdir(target_path):
                        if self.filter_sdb_file(f):
                            os.remove(self.get_sdb_file_path(f))
                            logger.info(f"sdb file {f} uninstalled.")
                            count += 1
                        else:
                            logger.error(f"Error: {f} is not a sdb file, can't uninstall, please check.")
                    source_path = pathlib.Path(target_path, "jidusdb")
                    if os.path.exists(source_path):
                        shutil.rmtree(source_path, onerror=self.read_only_handler)
                    if not count:
                        logger.error(f"Error: No file in {target_path}, please check.")
            else:
                logger.error(f"Error: No folder {target_path}, please check.")

    def show_sdb_file(self, 
                      filename: str=None,
                      sdb_version: str=None
                      ) -> None:

        if filename:
            if sdb_version:
                target_path = self.get_sdb_folder_path(sdb_version)
                if os.path.exists(target_path):
                    file_path = self.get_sdb_file_path(filename, sdb_version)
                    if os.path.exists(file_path):
                        if self.filter_sdb_file(filename):
                            logger.info(f"Get sdb file path: {file_path}")
                        else:
                            logger.error(f"Error: {filename} is not a sdb file, please check.")
                    else:
                        logger.error("Error: No this sdb file, please install.")
                else:
                    logger.error(f"Error: No folder {target_path}, please check.")
            else:
                file_path = self.get_sdb_file_path(filename, sdb_version)
                if os.path.exists(file_path):
                    if self.filter_sdb_file(filename):
                        logger.info(f"Get sdb file path: {file_path}")
                    else:
                        logger.error(f"Error: {filename} is not a sdb file, please check.")
                else:
                    logger.error("Error: No this sdb file, please install.")
        else:
            target_path = self.get_sdb_folder_path(sdb_version)
            if os.path.exists(target_path):
                logger.info(f"Get sdb folder path: {target_path}")
                count = 0
                for f in os.listdir(target_path):
                    if self.filter_sdb_file(f):
                        logger.info(f"Installed sdb file: {f}")
                        count += 1
                if count == 0:
                    logger.error("Error: No sdb file in this folder, please install.")
            else:
                logger.error(f"Error: No folder {target_path}, please check.")

    @abstractmethod
    def filter_sdb_file(self, filename: str) -> None:
        """Filter sdb file.

        Override this method to filter sdb file.

        :param filename: filename.
        
        :raises NotImplementedError:
            If an error occurred while filtering
        """
        raise NotImplementedError("sdb file not filtered!")

    @abstractmethod
    def validate_sdb_file(self, filename: str) -> None:
        """Validate sdb file.

        Override this method to validate sdb file.

        :param filename: filename.
        
        :raises NotImplementedError:
            If an error occurred while validating
        """
        raise NotImplementedError("sdb file not validated!")
    
    @abstractmethod
    def get_remote_sdb_path(self) -> None:
        """Get remote repository sdb file path.

        Override this method to get remote repository sdb file path.
        
        :raises NotImplementedError:
            If an error occurred while getting sdb file path
        """
        raise NotImplementedError("sdb file path not got!")


class CanSdbSystem(SdbSystemABC):

    def filter_sdb_file(self, filename: str) -> bool:
        if filename.endswith(".dbc"):
            return True
        else:
            return False

    def validate_sdb_file(self, filepath: str) -> bool:
        try:
            load_file(filepath)
            return True
        except:
            logger.error(f"Error: {os.path.basename(filepath)} is not a valid dbc file, please check.")
            return False
        
    def get_remote_sdb_path(self) -> None:
        can_sdb_file_path = "jidusdb/02-DBC/AddNmSigs"
        return can_sdb_file_path
             