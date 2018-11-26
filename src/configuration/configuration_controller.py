from subprocess import run, CalledProcessError
import os
from configobj import ConfigObj
from pathlib import Path
from shlex import quote
import json


class ConfigurationController:
    def __init__(self, params_path='', install_path=''):
        self._multichain_util_arg = ['./multichain-util']
        self._multichain_d_arg = ['./multichaind']
        self._multichain_cli_arg = ['multichain-cli']
        self._create = self._multichain_util_arg+['create']
        self._networkinfo_arg = 'getnetworkinfo'
        self._data_dir_arg = "-datadir="
        self._multichain_daemon = "-daemon"
        self._multichain_path = ".multichain/"
        self._params_file = "/params.dat"
        self._chain_description = "chain-description"
        self._max_block_size = "maximum-block-size"
        self._target_block_time = "target-block-time"
        self._mining_turnover = "mining-turnover"
        self._mining_diversity = "mining-diversity"
        self._default_install_path = '/usr/local/bin'
        self._params_path = self.validate_params_path(params_path)
        self._install_path = self.validate_install_path(install_path)
        self._localaddresses_arg = 'localaddresses'
        self._address_arg = 'address'
        self._default_network_port_arg = 'default-network-port'

    def create_chain(self,blockchain_name: str):
        """
        Creates a new blockcahin with the provided name.
        Returns messange acknowledging that blockchain has been succesfully created :
        MultiChain 2.0 alpha 5 Utilities (latest protocol 20004)

        Blockchain parameter set was successfully generated.
        You can edit it in /home/darshgrewal/.multichain/blockchain_name/params.dat before running multichaind for the first time.

        To generate blockchain please run "multichaind blockchain_name -daemon".
        """
        try:
            cmd = self._create + [blockchain_name]+[self._data_dir_arg+self._params_path]
            output = run(cmd, check=True, capture_output=True, cwd=self._install_path)
            return output.stdout.strip()
        except CalledProcessError as err:
            print(err.stderr)
        except Exception as err:
            print(err)

    def config_params(self, blockchain_name: str, params_dict:{}):

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
            config = ConfigObj(self._params_path+blockchain_name + self._params_file)

            for key in params_dict:
                config[key]=params_dict.get(key)
            config.write()
        except Exception as err:
            print(err)

    def deploy_blockchain(self, blockchain_name):
        """
        Intializes the blockchain and also creates the genesis block
        :param blockchain_name: Name of the blockchain that is to be  deployed
        :return: Confirmation message acknowledging the deployment of the blockchain
        """
        try:
            cmd = self._multichain_d_arg+[blockchain_name, self._multichain_daemon]+[self._data_dir_arg+self._params_path]
            run(cmd, timeout=5, cwd=self._install_path)
        except CalledProcessError as err:
            print(err.stderr)
        except Exception as err:
            print(err)

    def validate_params_path(self,path):
        """
        Validates the the params path provided by the user
        :return: a valid path of params.dat location
        """
        if os.path.exists(path):
            return path
        return os.path.join(str(Path.home()),self._multichain_path)

    def validate_install_path(self,path):
        """
        Validates the the isntall path provided by the user
        :return: a valid path of install path of MultiChain
        This is the default path of install which is generally used normal user programs that are not generally managed by the distribuation package manager
        """
        if os.path.exists(path):
            return path
        return self._default_install_path

    def get_node_address(self,blockchain_name: str):
        """
        Returns the node address for the specified blockchain in
        the fomart -> chain1@[ip-address]:[port]
        :param blockchain_name:
        :return:
        """

        try:
            cmd = self._multichain_cli_arg +[quote(blockchain_name)]+[self._networkinfo_arg]
            output = run(cmd, check=True, capture_output=True, cwd=self._install_path)
            json_output = json.loads(output.stdout.strip())
            ip_address = json_output[self._localaddresses_arg][0][self._address_arg]
            val = blockchain_name +'@'+ ip_address+':'+ self.get_config_param(blockchain_name, param=self._default_network_port_arg)
            return val
        except CalledProcessError as err:
            print(err.stderr)
        except Exception as err:
            print(err)

    def get_config_param(self,blockchain_name: str, param: str):
        """
        Returns the value for a specified parameter within in the param.dat file
        eg - value = config.get_config_param(blockchain_name=name,param='default-network-port')
        :param blockchain_name: name of the blockchain
        :param param: parameter to be changed
        :returns: Value of the parameter from the params.dat file
        """
        try:
            config = ConfigObj(self._params_path + blockchain_name + self._params_file)
            value = config[param]
            return value
        except Exception as err:
            print(err)

    def get_blockchains(self):
        """
        Provides a list of all the blockchains in the params path
        default in -> ~/.multichain
        :returns: a list containing string value that represents a blockchain
        """
        files = os.listdir(self._params_path)
        chains = []
        for chain in files:
            try:
                files = os.listdir(os.path.join(self._params_path, chain))
                if 'params.dat' in files:
                    chains.append(chain)
            except Exception as err:
                continue

        return chains