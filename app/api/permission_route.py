from flask import Flask, request, jsonify, Blueprint
from flask_api import status
from app.models.permission.permission_controller import PermissionController
from app.models.exception.multichain_error import MultiChainError

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
            return (
                jsonify({"error": "The request body is empty!"}),
                status.HTTP_204_NO_CONTENT
            )

        if not BLOCKCHAIN_NAME_FIELD_NAME in json_request:
            return (
                jsonify({"error": "The " + BLOCKCHAIN_NAME_FIELD_NAME + " field was not found in the request!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not ADDRESSES_FIELD_NAME in json_request:
            return (
                jsonify({"error": "The " + ADDRESSES_FIELD_NAME + " field was not found in the request!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not PERMISSIONS_FIELD_NAME in json_request:
            return (
                jsonify({"error": "The " + PERMISSIONS_FIELD_NAME + " field was not found in the request!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        blockchain_name = json_request[BLOCKCHAIN_NAME_FIELD_NAME]
        addresses = json_request[ADDRESSES_FIELD_NAME]
        permissions = json_request[PERMISSIONS_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            return (
                jsonify({"error": "The provided blockchain name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST
            )

        if not addresses:
            return (
                jsonify({"error": "The provided addresses can't be empty!"}),
                status.HTTP_400_BAD_REQUEST
            )

        if not permissions:
            return (
                jsonify({"error": "The provided permissions can't be empty!"}),
                status.HTTP_400_BAD_REQUEST
            )

        blockchain_name = blockchain_name.strip()
        output = (PermissionController.grant_global_permission(blockchain_name, addresses, permissions)).decode('utf-8')
        output = output[:-1]
        return jsonify({"Transaction ID": output}), status.HTTP_200_OK
    except ValueError as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST
    except Exception as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST


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
            return (
                jsonify({"error": "The request body is empty!"}),
                status.HTTP_204_NO_CONTENT
            )

        if not BLOCKCHAIN_NAME_FIELD_NAME in json_request:
            return (
                jsonify({"error": "The " + BLOCKCHAIN_NAME_FIELD_NAME + " field was not found in the request!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not ADDRESS_FIELD_NAME in json_request:
            return (
                jsonify({"error": "The " + ADDRESS_FIELD_NAME + " field was not found in the request!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not STREAM_NAME_FIELD_NAME in json_request:
            return (
                jsonify({"error": "The " + STREAM_NAME_FIELD_NAME + " field was not found in the request!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not PERMISSION_FIELD_NAME in json_request:
            return (
                jsonify({"error": "The " + PERMISSION_FIELD_NAME + " field was not found in the request!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        blockchain_name = json_request[BLOCKCHAIN_NAME_FIELD_NAME]
        address = json_request[ADDRESS_FIELD_NAME]
        stream_name = json_request[STREAM_NAME_FIELD_NAME]
        permission = json_request[PERMISSION_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            return (
                jsonify({"error": "The provided blockchain name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST
            )

        if not address or not address.strip():
            return (
                jsonify({"error": "The provided addresses can't be empty!"}),
                status.HTTP_400_BAD_REQUEST
            )

        if not stream_name or not stream_name.strip():
            return (
                jsonify({"error": "The provided stream name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST
            )

        if not permission or not permission.strip():
            return (
                jsonify({"error": "The provided permissions can't be empty!"}),
                status.HTTP_400_BAD_REQUEST
            )

        blockchain_name = blockchain_name.strip()
        address = address.strip()
        stream_name = stream_name.strip()
        permission = permission.strip()
        setting = PermissionController.grant_stream_permission(blockchain_name, address, stream_name, permission)\
            .decode('utf-8')
        setting = setting[:-1]
        return jsonify({"Transaction ID": setting}), status.HTTP_200_OK
    except ValueError as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST
    except Exception as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST


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
            return (
                jsonify({"error": "The request body is empty!"}),
                status.HTTP_204_NO_CONTENT
            )

        if not BLOCKCHAIN_NAME_FIELD_NAME in json_request:
            return (
                jsonify({"error": "The " + BLOCKCHAIN_NAME_FIELD_NAME + " field was not found in the request!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not ADDRESSES_FIELD_NAME in json_request:
            return (
                jsonify({"error": "The " + ADDRESSES_FIELD_NAME + " field was not found in the request!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not PERMISSIONS_FIELD_NAME in json_request:
            return (
                jsonify({"error": "The " + PERMISSIONS_FIELD_NAME + " field was not found in the request!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        blockchain_name = json_request[BLOCKCHAIN_NAME_FIELD_NAME]
        addresses = json_request[ADDRESSES_FIELD_NAME]
        permissions = json_request[PERMISSIONS_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            return (
                jsonify({"error": "The provided blockchain name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST
            )

        if not addresses or not addresses.strip():
            return (
                jsonify({"error": "The provided addresses can't be empty!"}),
                status.HTTP_400_BAD_REQUEST
            )

        if not permissions or not permissions.strip():
            return (
                jsonify({"error": "The provided permissions can't be empty!"}),
                status.HTTP_400_BAD_REQUEST
            )

        blockchain_name = blockchain_name.strip()
        addresses = addresses.strip()
        permissions = permissions.strip()

        output = PermissionController.revoke_global_permission(blockchain_name, addresses, permissions).decode('utf-8')
        output = output[:-1]

        return jsonify({"Transaction ID" : output}), status.HTTP_200_OK
    except ValueError as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST
    except Exception as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST




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
            return (
                jsonify({"error": "The request body is empty!"}),
                status.HTTP_204_NO_CONTENT
            )

        if not BLOCKCHAIN_NAME_FIELD_NAME in json_request:
            return (
                jsonify({"error": "The " + BLOCKCHAIN_NAME_FIELD_NAME + " field was not found in the request!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not ADDRESS_FIELD_NAME in json_request:
            return (
                jsonify({"error": "The " + ADDRESS_FIELD_NAME + " field was not found in the request!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not STREAM_NAME_FIELD_NAME in json_request:
            return (
                jsonify({"error": "The " + STREAM_NAME_FIELD_NAME + " field was not found in the request!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not PERMISSION_FIELD_NAME in json_request:
            return (
                jsonify({"error": "The " + PERMISSION_FIELD_NAME + " field was not found in the request!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        blockchain_name = json_request[BLOCKCHAIN_NAME_FIELD_NAME]
        address = json_request[ADDRESS_FIELD_NAME]
        stream_name = json_request[STREAM_NAME_FIELD_NAME]
        permission = json_request[PERMISSION_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            return (
                jsonify({"error": "The provided blockchain name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST
            )

        if not address or not address.strip():
            return (
                jsonify({"error": "The provided addresses can't be empty!"}),
                status.HTTP_400_BAD_REQUEST
            )

        if not stream_name or not stream_name.strip():
            return (
                jsonify({"error": "The provided stream name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST
            )

        if not permission or not permission.strip():
            return (
                jsonify({"error": "The provided permissions can't be empty!"}),
                status.HTTP_400_BAD_REQUEST
            )

        blockchain_name = blockchain_name.strip()
        address = address.strip()
        stream_name = stream_name.strip()
        permission = permission.strip()

        output =  PermissionController.revoke_stream_permission(blockchain_name, address, stream_name,
                                                                         permission).decode('utf-8')
        output = output[:-1]

        return jsonify({"Transaction ID" : output}), status.HTTP_200_OK
    except ValueError as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST
    except Exception as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST




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
            return (
                jsonify({"error": "The request body is empty!"}),
                status.HTTP_204_NO_CONTENT
            )

        if not BLOCKCHAIN_NAME_FIELD_NAME in json_request:
            return (
                jsonify({"error": "The " + BLOCKCHAIN_NAME_FIELD_NAME + " field was not found in the request!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not ADDRESSES_FIELD_NAME in json_request:
            return (
                jsonify({"error": "The " + ADDRESSES_FIELD_NAME + " field was not found in the request!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not PERMISSIONS_FIELD_NAME in json_request:
            return (
                jsonify({"error": "The " + PERMISSIONS_FIELD_NAME + " field was not found in the request!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not VERBOSE_FIELD_NAME in json_request:
            return (
                jsonify({"error": "The " + VERBOSE_FIELD_NAME + " field was not found in the request!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        blockchain_name = json_request[BLOCKCHAIN_NAME_FIELD_NAME]
        addresses = json_request[ADDRESSES_FIELD_NAME]
        permissions = json_request[PERMISSIONS_FIELD_NAME]
        verbose = json_request[VERBOSE_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            return (
                jsonify({"error": "The provided blockchain name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST
            )

        if not addresses:
            return (
                jsonify({"error": "The provided addresses can't be empty!"}),
                status.HTTP_400_BAD_REQUEST
            )

        if not verbose or not verbose.strip():
            return (
                jsonify({"error": "The verbose option can't be empty!"}),
                status.HTTP_400_BAD_REQUEST
            )

        if not verbose == "False" or not verbose == "True":
            return (
                jsonify({"error": "The verbose option must be a boolean!"}),
                status.HTTP_400_BAD_REQUEST
            )

        blockchain_name = blockchain_name.strip()

        if verbose == "True":
            verbose = True

        if verbose == "False":
            verbose = False

        output = (PermissionController.get_permissions(blockchain_name, permissions, addresses, verbose))

        return jsonify({"Transaction ID": output}), status.HTTP_200_OK
    except ValueError as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST
    except Exception as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST
