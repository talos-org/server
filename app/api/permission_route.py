from flask import Flask, request, jsonify, Blueprint
from flask_api import status
from app.models.permission.permission_controller import PermissionController
from app.models.exception.multichain_error import MultiChainError
import json

mod = Blueprint("permission", __name__)


BLOCKCHAIN_NAME_FIELD_NAME = "blockchainName"
ADDRESSES_FIELD_NAME = "addresses"
ADDRESS_FIELD_NAME = "address"
PERMISSIONS_FIELD_NAME = "permissions"
PERMISSION_FIELD_NAME = "permission"
STREAM_NAME_FIELD_NAME = "streamName"
VERBOSE_FIELD_NAME = "verbose"


"""
Grants global permissions to the provided addresses.
The following data is expected in the body of the request:
    "blockchainName": blockchain name
    "addresses": list of addresses
    "permissions": list of permissions
"""


@mod.route("/grant_global_permission", methods=["POST"])
def grant_global_permission():
    try:
        json_request = request.get_json()

        if not json_request:
            raise ValueError("The request body is empty!")

        if not BLOCKCHAIN_NAME_FIELD_NAME in json_request:
            raise ValueError(
                "The "
                + BLOCKCHAIN_NAME_FIELD_NAME
                + " field was not found in the request!"
            )

        if not ADDRESSES_FIELD_NAME in json_request:
            raise ValueError(
                "The " + ADDRESSES_FIELD_NAME + " field was not found in the request!"
            )

        if not PERMISSIONS_FIELD_NAME in json_request:
            raise ValueError(
                "The " + PERMISSIONS_FIELD_NAME + " field was not found in the request!"
            )

        blockchain_name = json_request[BLOCKCHAIN_NAME_FIELD_NAME]
        addresses = json_request[ADDRESSES_FIELD_NAME]
        permissions = json_request[PERMISSIONS_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The provided blockchain name can't be empty!")

        if not addresses:
            raise ValueError("The provided addresses can't be empty!")

        if not permissions:
            raise ValueError("The provided permissions can't be empty!")

        blockchain_name = blockchain_name.strip()
        output = (
            PermissionController.grant_global_permission(
                blockchain_name, addresses, permissions
            )
        ).decode("utf-8")
        output = output[:-1]
        return jsonify({"transactionID": output}), status.HTTP_200_OK
    except MultiChainError as ex:
        return jsonify(ex.get_info()), status.HTTP_400_BAD_REQUEST
    except (ValueError, Exception) as ex:
        return (jsonify({"error": {"message": str(ex)}}), status.HTTP_400_BAD_REQUEST)


"""
Grants stream permissions to the provided addresses and stream.
The following data is expected in the body of the request:
    "blockchainName": blockchain name
    "address": address
    "streamName": stream name
    "permission": permissions
"""


@mod.route("/grant_stream_permission", methods=["POST"])
def grant_stream_permission():
    try:
        json_request = request.get_json()

        if not json_request:
            raise ValueError("The request body is empty!")

        if not BLOCKCHAIN_NAME_FIELD_NAME in json_request:
            raise ValueError(
                "The "
                + BLOCKCHAIN_NAME_FIELD_NAME
                + " field was not found in the request!"
            )

        if not ADDRESS_FIELD_NAME in json_request:
            raise ValueError(
                "The " + ADDRESS_FIELD_NAME + " field was not found in the request!"
            )

        if not STREAM_NAME_FIELD_NAME in json_request:
            raise ValueError(
                "The " + STREAM_NAME_FIELD_NAME + " field was not found in the request!"
            )

        if not PERMISSION_FIELD_NAME in json_request:
            raise ValueError(
                "The " + PERMISSION_FIELD_NAME + " field was not found in the request!"
            )

        blockchain_name = json_request[BLOCKCHAIN_NAME_FIELD_NAME]
        address = json_request[ADDRESS_FIELD_NAME]
        stream_name = json_request[STREAM_NAME_FIELD_NAME]
        permission = json_request[PERMISSION_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The provided blockchain name can't be empty!")

        if not address or not address.strip():
            raise ValueError("The provided addresses can't be empty!")

        if not stream_name or not stream_name.strip():
            raise ValueError("The provided stream name can't be empty!")

        if not permission or not permission.strip():
            raise ValueError("The provided permissions can't be empty!")

        blockchain_name = blockchain_name.strip()
        address = address.strip()
        stream_name = stream_name.strip()
        permission = permission.strip()
        transaction_id = PermissionController.grant_stream_permission(
            blockchain_name, address, stream_name, permission
        ).decode("utf-8")
        transaction_id = transaction_id[:-1]
        return jsonify({"transactionID": transaction_id}), status.HTTP_200_OK
    except MultiChainError as ex:
        return jsonify(ex.get_info()), status.HTTP_400_BAD_REQUEST
    except (ValueError, Exception) as ex:
        return (jsonify({"error": {"message": str(ex)}}), status.HTTP_400_BAD_REQUEST)


"""
Revokes global permissions to the provided addresses.
The following data is expected in the body of the request:
    "blockchainName": blockchain name
    "addresses": list of addresses
    "permissions": list of permissions
"""


@mod.route("/revoke_global_permission", methods=["POST"])
def revoke_global_permission():
    try:
        json_request = request.get_json()

        if not json_request:
            raise ValueError("The request body is empty!")

        if not BLOCKCHAIN_NAME_FIELD_NAME in json_request:
            raise ValueError(
                "The "
                + BLOCKCHAIN_NAME_FIELD_NAME
                + " field was not found in the request!"
            )

        if not ADDRESSES_FIELD_NAME in json_request:
            raise ValueError(
                "The " + ADDRESSES_FIELD_NAME + " field was not found in the request!"
            )

        if not PERMISSIONS_FIELD_NAME in json_request:
            raise ValueError(
                "The " + PERMISSIONS_FIELD_NAME + " field was not found in the request!"
            )

        blockchain_name = json_request[BLOCKCHAIN_NAME_FIELD_NAME]
        addresses = json_request[ADDRESSES_FIELD_NAME]
        permissions = json_request[PERMISSIONS_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The provided blockchain name can't be empty!")

        if not addresses or not addresses.strip():
            raise ValueError("The provided addresses can't be empty!")

        if not permissions or not permissions.strip():
            raise ValueError("The provided permissions can't be empty!")

        blockchain_name = blockchain_name.strip()
        addresses = addresses.strip()
        permissions = permissions.strip()

        transaction_id = PermissionController.revoke_global_permission(
            blockchain_name, addresses, permissions
        ).decode("utf-8")
        transaction_id = transaction_id[:-1]

        return jsonify({"transactionID": transaction_id}), status.HTTP_200_OK
    except MultiChainError as ex:
        return jsonify(ex.get_info()), status.HTTP_400_BAD_REQUEST
    except (ValueError, Exception) as ex:
        return (jsonify({"error": {"message": str(ex)}}), status.HTTP_400_BAD_REQUEST)


"""
Revoke stream permissions to the provided addresses and stream.
The following data is expected in the body of the request:
    "blockchainName": blockchain name
    "address": address
    "streamName": stream name
    "permission": permissions
"""


@mod.route("/revoke_stream_permission", methods=["POST"])
def revoke_stream_permission():
    try:
        json_request = request.get_json()

        if not json_request:
            raise ValueError("The request body is empty!")

        if not BLOCKCHAIN_NAME_FIELD_NAME in json_request:
            raise ValueError(
                "The "
                + BLOCKCHAIN_NAME_FIELD_NAME
                + " field was not found in the request!"
            )

        if not ADDRESS_FIELD_NAME in json_request:
            raise ValueError(
                "The " + ADDRESS_FIELD_NAME + " field was not found in the request!"
            )

        if not STREAM_NAME_FIELD_NAME in json_request:
            raise ValueError(
                "The " + STREAM_NAME_FIELD_NAME + " field was not found in the request!"
            )

        if not PERMISSION_FIELD_NAME in json_request:
            raise ValueError(
                "The " + PERMISSION_FIELD_NAME + " field was not found in the request!"
            )

        blockchain_name = json_request[BLOCKCHAIN_NAME_FIELD_NAME]
        address = json_request[ADDRESS_FIELD_NAME]
        stream_name = json_request[STREAM_NAME_FIELD_NAME]
        permission = json_request[PERMISSION_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The provided blockchain name can't be empty!")

        if not address or not address.strip():
            raise ValueError("The provided addresses can't be empty!")

        if not stream_name or not stream_name.strip():
            raise ValueError("The provided stream name can't be empty!")

        if not permission or not permission.strip():
            raise ValueError("The provided permissions can't be empty!")

        blockchain_name = blockchain_name.strip()
        address = address.strip()
        stream_name = stream_name.strip()
        permission = permission.strip()

        transaction_id = PermissionController.revoke_stream_permission(
            blockchain_name, address, stream_name, permission
        ).decode("utf-8")
        transaction_id = transaction_id[:-1]

        return jsonify({"transactionID": transaction_id}), status.HTTP_200_OK
    except MultiChainError as ex:
        return jsonify(ex.get_info()), status.HTTP_400_BAD_REQUEST
    except (ValueError, Exception) as ex:
        return (jsonify({"error": {"message": str(ex)}}), status.HTTP_400_BAD_REQUEST)


"""
Gets the permissions of the provided addresses, 
omit permissions to view all permissions, otherwise specific permissions can be passed
The following data is expected in the body of the request:
    "blockchainName": blockchain name
    "addresses": list of addresses
    "permissions": list of permissions
    "verbose": verbose boolean
"""


@mod.route("/get_permissions", methods=["POST"])
def get_permissions():
    try:
        json_request = request.get_json()

        if not json_request:
            raise ValueError("The request body is empty!")

        if not BLOCKCHAIN_NAME_FIELD_NAME in json_request:
            raise ValueError(
                "The "
                + BLOCKCHAIN_NAME_FIELD_NAME
                + " field was not found in the request!"
            )

        if not ADDRESSES_FIELD_NAME in json_request:
            raise ValueError(
                "The " + ADDRESSES_FIELD_NAME + " field was not found in the request!"
            )

        if not PERMISSIONS_FIELD_NAME in json_request:
            raise ValueError(
                "The " + PERMISSIONS_FIELD_NAME + " field was not found in the request!"
            )

        if not VERBOSE_FIELD_NAME in json_request:
            raise ValueError(
                "The " + VERBOSE_FIELD_NAME + " field was not found in the request!"
            )

        blockchain_name = json_request[BLOCKCHAIN_NAME_FIELD_NAME]
        addresses = json_request[ADDRESSES_FIELD_NAME]
        permissions = json_request[PERMISSIONS_FIELD_NAME]
        verbose = json_request[VERBOSE_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The provided blockchain name can't be empty!")

        if not addresses:
            raise ValueError("The provided addresses can't be empty!")

        if not verbose or not verbose.strip():
            raise ValueError("The verbose option can't be empty!")

        blockchain_name = blockchain_name.strip()

        if verbose == "True":
            verbose = True

        elif verbose == "False":
            verbose = False

        else:
            raise ValueError("The verbose option must be a boolean!")

        output = PermissionController.get_permissions(
            blockchain_name, permissions, addresses, verbose
        )

        return jsonify({"Permissions": output}), status.HTTP_200_OK
    except MultiChainError as ex:
        return jsonify(ex.get_info()), status.HTTP_400_BAD_REQUEST
    except (ValueError, Exception) as ex:
        return (jsonify({"error": {"message": str(ex)}}), status.HTTP_400_BAD_REQUEST)

