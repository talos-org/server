from subprocess import run, CalledProcessError
from app.models.exception.multichain_error import MultiChainError
import json


class PermissionController:
    MULTICHAIN_ARG = "multichain-cli"
    GRANT_ARG = "grant"
    REVOKE_ARG = "revoke"
    GET_PERMISSION_ARG = "listpermissions"
    GLOBAL_PERMISSIONS_LIST = {
        "connect",
        "send",
        "receive",
        "issue",
        "create",
        "issue",
        "mine",
        "activate",
        "admin",
    }
    STREAM_PERMISSIONS_LIST = {"write", "activate", "admin"}

    @staticmethod
    def grant_global_permission(
        blockchain_name: str, addresses: list, permissions: list
    ):
        """
        Grants permissions to a list of addresses. 
        Set permissions to a list of connect, send, receive, create, issue, mine, 
        activate, admin. 
        Returns the txid of the transaction granting the permissions.
        """
        try:
            blockchain_name = blockchain_name.strip()
            if not blockchain_name:
                raise ValueError("Blockchain name can't be empty")

            addresses = [address.strip() for address in addresses if address.strip()]
            if not addresses:
                raise ValueError("The list of addresses is empty")

            permissions = [
                permission.strip() for permission in permissions if permission.strip()
            ]
            if not permissions:
                raise ValueError("The list of permissions is empty")

            if not set(permissions).issubset(
                PermissionController.GLOBAL_PERMISSIONS_LIST
            ):
                raise ValueError(
                    "The permission(s) proivded: " + permissions + " does not exist."
                )

            args = [
                PermissionController.MULTICHAIN_ARG,
                blockchain_name,
                PermissionController.grant_global_permission,
                ",".join(addresses),
                ",".join(permissions),
            ]
            output = run(args, check=True, capture_output=True)

            return output.stdout
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            raise err

    @staticmethod
    def grant_stream_permission(
        blockchain_name: str, address: str, stream_name: str, permission: str
    ):
        """
        Grants permission to an address for a stream. set permission to one of write, 
        activate, admin.
        Returns the txid of the transaction granting the permissions.
        """
        try:
            blockchain_name = blockchain_name.strip()
            if not blockchain_name:
                raise ValueError("Blockchain name can't be empty")

            address = address.strip()
            stream_name = stream_name.strip()
            permission = permission.strip()

            if not address:
                raise ValueError("The address is empty")
            if not stream_name:
                raise ValueError("The stream name is empty")
            if not permission:
                raise ValueError("The permisison is empty")

            if permission.lower() not in PermissionController.STREAM_PERMISSIONS_LIST:
                raise ValueError(
                    "The permission provided:" + permission + " does not exist."
                )

            args = [
                PermissionController.MULTICHAIN_ARG,
                blockchain_name,
                PermissionController.grant_global_permission,
                address,
                stream_name + "." + permission.lower(),
            ]
            output = run(args, check=True, capture_output=True)

            return output.stdout
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            raise err

    @staticmethod
    def get_permissions(
        blockchain_name: str,
        permissions: list = None,
        addresses: list = None,
        verbose: bool = False,
    ):
        """
        Returns a list of all permissions which have been explicitly granted to addresses. 
        To list information about specific global permissions, set permissions to a list of connect, 
        send, receive, issue, mine, activate, admin. Omit to list all global permissions. 
        Provide a list in addresses to list the permissions for particular addresses or omit for all addresses. 
        If verbose is true, the admins output field lists the administrator/s who assigned the corresponding permission, 
        and the pending field lists permission changes which are waiting to reach consensus.
        """
        try:
            blockchain_name = blockchain_name.strip()
            if not blockchain_name:
                raise ValueError("Blockchain name can't be empty")

            permission_selector = "*"
            if permissions is not None:
                permissions = [
                    permission.strip()
                    for permission in permissions
                    if permission.strip()
                ]
                if not permissions:
                    raise ValueError("The list of permissions is empty")
                if not set(permissions).issubset(
                    PermissionController.GLOBAL_PERMISSIONS_LIST
                ):
                    raise ValueError(
                        "The permission(s) proivded: "
                        + permissions
                        + " does not exist."
                    )
                else:
                    permission_selector = ",".join(permissions)

            address_selector = "*"
            if addresses is not None:
                addresses = [
                    address.strip() for address in addresses if address.strip()
                ]
                if not addresses:
                    raise ValueError("The list of addresses is empty")
                address_selector = ",".join(addresses)

            args = [
                PermissionController.MULTICHAIN_ARG,
                blockchain_name,
                PermissionController.GET_PERMISSION_ARG,
                permission_selector,
                address_selector,
                json.dumps(verbose),
            ]
            output = run(args, check=True, capture_output=True)

            return json.loads(output.stdout)
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            raise err

    @staticmethod
    def revoke_global_permission(
        blockchain_name: str, addresses: list, permissions: list
    ):
        """
        Revokes permissions from a list of addresses. 
        Set permissions to a list of connect, send, receive, create, issue, mine, 
        activate, admin. 
        Returns the txid of transaction revoking the permissions. 
        """
        try:
            blockchain_name = blockchain_name.strip()
            if not blockchain_name:
                raise ValueError("Blockchain name can't be empty")

            addresses = [address.strip() for address in addresses if address.strip()]
            if not addresses:
                raise ValueError("The list of addresses is empty")

            permissions = [
                permission.strip() for permission in permissions if permission.strip()
            ]
            if not permissions:
                raise ValueError("The list of permissions is empty")

            if not set(permissions).issubset(
                PermissionController.GLOBAL_PERMISSIONS_LIST
            ):
                raise ValueError(
                    "The permission(s) proivded: " + permissions + " does not exist."
                )

            args = [
                PermissionController.MULTICHAIN_ARG,
                blockchain_name,
                PermissionController.REVOKE_ARG,
                ",".join(addresses),
                ",".join(permissions),
            ]
            output = run(args, check=True, capture_output=True)

            return output.stdout
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            raise err

    @staticmethod
    def revoke_stream_permission(
        blockchain_name: str, address: str, stream_name: str, permission: str
    ):
        """
        Revokes permissions from an address for a stream. 
        set permission to one of write, activate, admin.
        Returns the txid of transaction revoking the permissions. 
        """
        try:
            blockchain_name = blockchain_name.strip()
            if not blockchain_name:
                raise ValueError("Blockchain name can't be empty")

            address = address.strip()
            stream_name = stream_name.strip()
            permission = permission.strip()

            if not address:
                raise ValueError("The address is empty")

            if not stream_name:
                raise ValueError("The stream name is empty")

            if not permission:
                raise ValueError("The permission is empty")

            if permission.lower() not in PermissionController.STREAM_PERMISSIONS_LIST:
                raise ValueError(
                    "The permission provided: " + permission + " does not exist."
                )

            args = [
                PermissionController.MULTICHAIN_ARG,
                blockchain_name,
                PermissionController.REVOKE_ARG,
                address,
                stream_name + "." + permission.lower(),
            ]
            output = run(args, check=True, capture_output=True)

            return output.stdout
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            raise err

