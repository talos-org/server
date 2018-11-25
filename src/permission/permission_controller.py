from subprocess import run, CalledProcessError
from shlex import quote
import json


class PermissionController:

    def __init__(self, blockchain_name: str):
        self._multichain_arg = ['multichain-cli', quote(blockchain_name)]
        self._grant_arg = self._multichain_arg + ['grant']
        self._revoke_arg = self._multichain_arg + ['revoke']
        self._get_permissions_arg = self._multichain_arg + ['listpermissions']
        self._GLOBAL_PERMISSIONS_LIST = {'connect', 'send', 'receive',
                                         'issue', 'create', 'issue', 'mine', 'activate', 'admin'}
        self._STREAM_PERMISSIONS_LIST = {'write', 'activate', 'admin'}

    def grant_global_permission(self, addresses: list, permissions: list):
        """
        Grants permissions to a list of addresses. 
        Set permissions to a list of connect, send, receive, create, issue, mine, 
        activate, admin. 
        Returns the txid of the transaction granting the permissions.
        """
        try:
            if not set(permissions).issubset(self._GLOBAL_PERMISSIONS_LIST):
                raise ValueError('The permission(s) proivded: ' +
                                 permissions + ' does not exist.')

            
            args = self._grant_arg + \
                [quote(','.join(addresses)), quote(','.join(permissions))]
            output = run(args, check=True, capture_output=True)

            return output.stdout
        except CalledProcessError as err:
            print(err.stderr)
        except Exception as err:
            print(err)

    def grant_stream_permission(self, address: str, stream_name: str, permission: str):
        """
        Grants permission to an address for a stream. set permission to one of write, 
        activate, admin.
        Returns the txid of the transaction granting the permissions.
        """
        try:
            if permission.lower() not in self._STREAM_PERMISSIONS_LIST:
                raise ValueError('The permission provided:' +
                                 permission + ' does not exist.')

            args = self._grant_arg + \
                [quote(address), quote(
                    stream_name + '.' + permission.lower())]
            output = run(args, check=True, capture_output=True)

            return output.stdout
        except CalledProcessError as err:
            print(err.stderr)
        except Exception as err:
            print(err)

    def get_permissions(self, permissions: list = None, addresses: list = None, verbose: bool = False):
        """
        Returns a list of all permissions which have been explicitly granted to addresses. 
        To list information about specific global permissions, set permissions to a list of connect, 
        send, receive, issue, mine, activate, admin. Omit to list all global permissions. 
        Provide a list in addresses to list the permissions for particular addresses or omit for all addresses. 
        If verbose is true, the admins output field lists the administrator/s who assigned the corresponding permission, 
        and the pending field lists permission changes which are waiting to reach consensus.
        """
        try:

            permission_selector = '*'
            if permissions is not None:
                if not set(permissions).issubset(self._GLOBAL_PERMISSIONS_LIST):
                    raise ValueError(
                        'The permission(s) proivded: ' + permissions + ' does not exist.')
                else:
                    permission_selector = quote(','.join(permissions))

            address_selector = '*'
            if addresses is not None:
                address_selector = quote(','.join(addresses))

            args = self._get_permissions_arg + \
                [permission_selector, address_selector, json.dumps(verbose)]
            output = run(args, check=True, capture_output=True)

            return json.loads(output.stdout)
        except CalledProcessError as err:
            print(err.stderr)
        except Exception as err:
            print(err)
    

    def revoke_global_permission(self, addresses: list, permissions: list):
        """
        Revokes permissions from a list of addresses. 
        Set permissions to a list of connect, send, receive, create, issue, mine, 
        activate, admin. 
        Returns the txid of transaction revoking the permissions. 
        """
        try:
            if not set(permissions).issubset(self._GLOBAL_PERMISSIONS_LIST):
                raise ValueError('The permission(s) proivded: ' +
                                 permissions + ' does not exist.')

            
            args = self._revoke_arg + \
                [quote(','.join(addresses)), quote(','.join(permissions))]
            output = run(args, check=True, capture_output=True)

            return output.stdout
        except CalledProcessError as err:
            print(err.stderr)
        except Exception as err:
            print(err)
    
    def revoke_stream_permission(self, address: str, stream_name: str, permission: str):
        """
        Revokes permissions from an address for a stream. 
        set permission to one of write, activate, admin.
        Returns the txid of transaction revoking the permissions. 
        """
        try:
            if permission.lower() not in self._STREAM_PERMISSIONS_LIST:
                raise ValueError('The permission provided: ' +
                                 permission + ' does not exist.')

            args = self._revoke_arg + \
                [quote(address), quote(
                    stream_name + '.' + permission.lower())]
            output = run(args, check=True, capture_output=True)

            return output.stdout
        except CalledProcessError as err:
            print(err.stderr)
        except Exception as err:
            print(err)
