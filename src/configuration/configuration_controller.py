from subprocess import run, CalledProcessError
import os
from configparser import RawConfigParser
from configobj import ConfigObj
from pathlib import Path

class ConfiguartionController:
    def __init__(self, params_path='', install_path=''):
        self._multichain_util_arg = ['./multichain-util']
        self._multichain_d_arg = ['./multichaind']
        self._create = self._multichain_util_arg+['create']
        self._data_dir_arg = "-datadir="
        self._multichain_daemon = "-daemon"
        self._multichain_path = "/.multichain/"
        self._params_file = "/params.dat"
        self._chain_description = "chain-description"
        self._max_block_size = "maximum-block-size"
        self._target_block_time = "target-block-time"
        self._mining_turnover = "mining-turnover"
        self._mining_diversity = "mining-diversity"
        self._dummy_section = 'dummy_section'
        self._params_path = self.validate_params_path(params_path)
        self._install_path = self.validate_install_path(install_path)

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
        return str(Path.home())+self._multichain_path

    def validate_install_path(self,path):
        """
        Validates the the isntall path provided by the user
        :return: a valid path of install path of MultiChain
        """
        if os.path.exists(path):
            return path
        return '/usr/local/bin'#This is the default path of install which is generally used normal user programs that are not generally managed by the distribuation package manager