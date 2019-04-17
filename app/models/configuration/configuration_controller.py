import os
from app.models.exception.multichain_error import MultiChainError
import subprocess
from configobj import ConfigObj
from pathlib import Path
from shlex import quote
import json


class ConfigurationController:
    MULTICHAIN_UTIL_ARG = ["./multichain-util"]
    MULTICHAIN_D_ARG = ["./multichaind"]
    MULTICHAIN_CLI_ARG = ["./multichain-cli"]
    CREATE_ARG = MULTICHAIN_UTIL_ARG + ["create"]
    NETWORKINFO_ARG = "getnetworkinfo"
    DATA_DIR_ARG = "-datadir="
    MULTICHAIN_DAEMON = "-daemon"
    MULTICHAIN_PATH = ".multichain/"
    PARAMS_FILE = "/params.dat"
    CHAIN_DESCRIPTION = "chain-description"
    MAX_BLOCK_SIZE = "maximum-block-size"
    TARGET_BLOCK_TIME = "target-block-time"
    MINING_TURNOVER = "mining-turnover"
    MINING_DIVERSITY = "mining-diversity"
    DEFAULT_INSTALL_PATH = "/usr/local/bin"
    GENESIS_BLOCK_FOUND_ARG = "Genesis block found"
    RETRIEVING_BLOCKCHAIN_ARG = "Retrieving blockchain parameters"
    LOCAL_ADDRESSES_ARG = "localaddresses"
    ADDRESS_ARG = "address"
    DEFAULT_NETWORK_PORT_ARG = "default-network-port"
    MINE_EMPTY_ROUNDS = "mine-empty-rounds"
    MINE_EMPTY_ROUNDS_VALUE = "1"

    @staticmethod
    def create_chain(blockchain_name: str, params_path="", install_path=""):

        """
        Creates a new blockcahin with the provided name.
        Returns messange acknowledging that blockchain has been succesfully created :
        MultiChain 2.0 alpha 5 Utilities (latest protocol 20004)

        Blockchain parameter set was successfully generated.
        You can edit it in /home/darshgrewal/.multichain/blockchain_name/params.dat before running multichaind for the first time.

        To generate blockchain please run "multichaind blockchain_name -daemon".
        """
        try:
            cmd = (
                ConfigurationController.CREATE_ARG
                + [blockchain_name]
                + [
                    ConfigurationController.DATA_DIR_ARG
                    + ConfigurationController.validate_params_path(params_path)
                ]
            )
            output = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                cwd=ConfigurationController.validate_install_path(install_path),
            )
            config = ConfigObj(
                ConfigurationController.validate_params_path(params_path)
                + blockchain_name
                + ConfigurationController.PARAMS_FILE
            )
            config[
                ConfigurationController.MINE_EMPTY_ROUNDS
            ] = ConfigurationController.MINE_EMPTY_ROUNDS_VALUE
            config.write()
            return output.stdout.strip()
        except subprocess.CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            raise err

    @staticmethod
    def config_params(blockchain_name: str, params_dict: {}, params_path=""):

        """
        The following parameters of a blockchain can be be configured after creating the chain but before starting the chain.
        The parameters are set in the params.dat file for each blockchain, and once the blockchain has been intialized these parameters can not be changed.
        :param blockchain_name: Blockchain to be changed
        :param description: Textual description of the blockchain for display to users.
        :param max_block_size: Maximum number of bytes in each block, to prevent network flooding by a rogue block creator.
        :param target_block_time: Target average number of seconds between blocks
        :param mining_turnover:A value of 0.0 prefers a pure round robin scheme between an automatically-discovered subset of the addresses with mine permissions,
        with others stepping in only if one fails. A value of 1.0 prefers pure random block creation between these addresses. Intermediate values set the balance
        between these two behaviors. Lower values reduce the number of forks, making the blockchain more efficient, but increase the level of validator concentration.
        :param mining_diversity:Minimum proportion of permitted “miners” required to participate in the round-robin scheme to render a valid blockchain, between 0.0 (no constraint)
        and 1.0 (every address with mine permissions must participate).
        :return Confirmation messange acknowledging that the parameters have been successfully added to the params.data file:
        """
        try:
            config = ConfigObj(
                ConfigurationController.validate_params_path(params_path)
                + blockchain_name
                + ConfigurationController.PARAMS_FILE
            )

            for key in params_dict:
                if key == ConfigurationController.MINING_TURNOVER and float(
                    params_dict.get(key)
                ) in range(0.0, 1.0):
                    config[key] = params_dict.get(key)
                elif key == ConfigurationController.MINING_DIVERSITY and float(
                    params_dict.get(key)
                ) in range(0.0, 1.0):
                    config[key] = params_dict.get(key)
                elif key == ConfigurationController.TARGET_BLOCK_TIME and int(
                    params_dict.get(key)
                ) in range(9, 60):
                    config[key] = params_dict.get(key)
            config.write()
        except Exception as err:
            raise err

    @staticmethod
    def deploy_blockchain(blockchain_name, params_path="", install_path=""):
        """
        Intializes the blockchain and also creates the genesis block
        :param blockchain_name: Name of the blockchain that is to be  deployed
        :return: Boolean value  acknowledging the deployment of the blockchain
        cwd=self._install_path
        """
        try:
            cmd = (
                ConfigurationController.MULTICHAIN_D_ARG
                + [blockchain_name, ConfigurationController.MULTICHAIN_DAEMON]
                + [
                    ConfigurationController.DATA_DIR_ARG
                    + ConfigurationController.validate_params_path(params_path)
                ]
            )

            p = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=ConfigurationController.validate_install_path(install_path),
            )

            output = []
            for index, line in enumerate(p.stdout, start=1):
                output.append(line)
                if (ConfigurationController.GENESIS_BLOCK_FOUND_ARG in str(line)) or (
                    ConfigurationController.RETRIEVING_BLOCKCHAIN_ARG in str(line)
                ):
                    return True
                if index > 6:
                    return False

        except subprocess.CalledProcessError as err:
            raise err.stderr
        except Exception as err:
            raise err

    @staticmethod
    def validate_params_path(path):
        """
        Validates the the params path provided by the user
        :return: a valid path of params.dat location
        """
        if os.path.exists(path):
            return path
        return os.path.join(str(Path.home()), ConfigurationController.MULTICHAIN_PATH)

    @staticmethod
    def validate_install_path(path):
        """
        Validates the the isntall path provided by the user
        :return: a valid path of install path of MultiChain
        This is the default path of install which is generally used normal user programs that are not generally managed by the distribuation package manager
        """
        if os.path.exists(path):
            return path
        return ConfigurationController.DEFAULT_INSTALL_PATH

    @staticmethod
    def get_node_address(blockchain_name: str, install_path=""):
        """
        Returns the node address for the specified blockchain in
        the fomart -> chain1@[ip-address]:[port]
        :param blockchain_name:
        :return:
        """

        try:
            cmd = (
                ConfigurationController.MULTICHAIN_CLI_ARG
                + [quote(blockchain_name)]
                + [ConfigurationController.NETWORKINFO_ARG]
            )
            output = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                cwd=ConfigurationController.validate_install_path(install_path),
            )
            json_output = json.loads(output.stdout.strip())
            print(type(json_output))
            ip_address = json_output[ConfigurationController.LOCAL_ADDRESSES_ARG][0][
                ConfigurationController.ADDRESS_ARG
            ]
            val = (
                blockchain_name
                + "@"
                + ip_address
                + ":"
                + ConfigurationController.get_config_param(
                    blockchain_name,
                    param=ConfigurationController.DEFAULT_NETWORK_PORT_ARG,
                )
            )
            return val
        except subprocess.CalledProcessError as err:
            raise err.stderr
        except Exception as err:
            raise err

    @staticmethod
    def get_config_param(blockchain_name: str, param: str, params_path=""):
        """
        Returns the value for a specified parameter within in the param.dat file
        eg - value = config.get_config_param(blockchain_name=name,param='default-network-port')
        :param blockchain_name: name of the blockchain
        :param param: parameter to be changed
        :returns: Value of the parameter from the params.dat file
        """
        try:
            config = ConfigObj(
                ConfigurationController.validate_params_path(params_path)
                + blockchain_name
                + ConfigurationController.PARAMS_FILE
            )
            value = config[param]
            return value
        except Exception as err:
            raise err

    @staticmethod
    def get_blockchains(params_path=""):
        """
        Provides a list of all the blockchains in the params path
        default in -> ~/.multichain
        :returns: a list containing string value that represents a blockchain
        """
        files = os.listdir(ConfigurationController.validate_params_path(params_path))
        chains = []
        for chain in files:
            try:
                files = os.listdir(
                    os.path.join(
                        ConfigurationController.validate_params_path(params_path), chain
                    )
                )
                if "params.dat" in files:
                    chains.append(chain)
            except Exception as err:
                continue

        return chains
