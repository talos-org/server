from plumbum import local, FG, BG, TF, RETCODE, ProcessExecutionError
import subprocess


class ConfiguartionController:
    def __init__(self):
        self._multichain_util = local['multichain-util']
        self._multichain_d = 'multichaind'
        self._multichain_daemon = "-daemon"
        self._create = self._multichain_util['create']
        self._multichain_path = "~/.multichain/"
        self._params_file = "/params.dat"
        self._chain_description = "chain-description = "
        self._max_block_size = "maximum-block-size = "
        self._target_block_time = "target-block-time = "
        self._mining_turnover = "mining-turnover = "
        self._mining_diversity = "mining-diversity = "

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
            output = self._create[blockchain_name].run(retcode=0)
            return output[1].strip()
        except ProcessExecutionError as err:
            print(err.args[3])
        except Exception as err:
            print(err)

    def config_params(self, blockchain_name=None,description=None, max_block_size=None, target_block_time=None, mining_turnover=None, mining_diversity=None):
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
            path = local[self._multichain_path+blockchain_name+self._params_file]
            file = open(str(path), 'r')
            lines = file.readlines()
            file.close()
            file2 = open(str(path), 'w')
            for line in lines:
                if (description is not None) & (self._chain_description in line):
                    line = self._chain_description + description+"\n"
                if (max_block_size is not None) & (self._max_block_size in line):
                    line = self._max_block_size + max_block_size+"\n"
                if (target_block_time is not None) & (self._target_block_time in line):
                    line = self._target_block_time + target_block_time+"\n"
                if (mining_turnover is not None) & (self._mining_turnover in line):
                    line = self._mining_diversity + mining_turnover+"\n"
                if (mining_diversity is not None) & (self._mining_diversity in line):
                    line = self._mining_diversity + mining_diversity+"\n"
                file2.write(line)
            file2.close()
        except Exception as err:
            print(err)

    def deploy_blockchain(self, blockchain_name):
        """
        Intializes the blockchain and also creates the genesis block
        :param blockchain_name: Name of the blockchain that is to be  deployed
        :return: Confirmation message acknowledging the deployment of the blockchain
        """

        try:
            cmd = [self._multichain_d,blockchain_name, self._multichain_daemon]
            subprocess.run(cmd, timeout=5)
        except ProcessExecutionError as err:
            print(err.args[3])
        except Exception as err:
            print(err)
