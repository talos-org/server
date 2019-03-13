from flask import Flask, request, jsonify, Blueprint
from flask_api import status
from app.models.permission.permission_controller import PermissionController
from app.models.exception.multichain_error import MultiChainError
import json
from flask_restplus import Namespace, Resource, reqparse, inputs, fields

BLOCKCHAIN_NAME_FIELD_NAME = "blockchainName"
ADDRESSES_FIELD_NAME = "addresses"
ADDRESS_FIELD_NAME = "address"
PERMISSIONS_FIELD_NAME = "permissions"
PERMISSION_FIELD_NAME = "permission"
STREAM_NAME_FIELD_NAME = "streamName"
VERBOSE_FIELD_NAME = "verbose"

permission_ns = Namespace("permissions", description="Permissions API")



permission_model = permission_ns.model(
    "Permission",
    {
        BLOCKCHAIN_NAME_FIELD_NAME: fields.String(
            required=True, description="The blockchain name"
        ),
    },
)


global_permission_model = permission_ns.clone(
    "Global permission",
    permission_model,
    {ADDRESSES_FIELD_NAME: fields.List(fields.String, required=True, description="list of addresses")},
    {PERMISSIONS_FIELD_NAME: fields.List(fields.String, required=True, description="list of permissions")},
)


@permission_ns.route("/grant_global_permission")
class GrantGlobalPermission(Resource):
    @permission_ns.expect(global_permission_model, validate=True)
    @permission_ns.doc(
        responses={
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_200_OK: "SUCCESS",
        }
    )
    def post(self):
        """
        Grants global permissions to the provided addresses.
        """
        blockchain_name = permission_ns.payload[BLOCKCHAIN_NAME_FIELD_NAME]
        addresses = permission_ns.payload[ADDRESSES_FIELD_NAME]
        permissions = permission_ns.payload[PERMISSIONS_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The provided blockchain name can't be empty!")

        blockchain_name = blockchain_name.strip()
        output = (
            PermissionController.grant_global_permission(
                blockchain_name, addresses, permissions
            )
        ).decode("utf-8")
        output = output[:-1]
        return {"transactionID": output}, status.HTTP_200_OK


stream_permission_model = permission_ns.clone(
    "Stream permission",
    permission_model,
    {ADDRESS_FIELD_NAME: fields.String(required=True, description="stream name")},
    {PERMISSION_FIELD_NAME: fields.String(required=True, description="permission name")},
    {STREAM_NAME_FIELD_NAME: fields.String(required=True, description="stream name")},
)


@permission_ns.route("/grant_stream_permission")
class GrantStreamPermission(Resource):
    @permission_ns.expect(stream_permission_model, validate=True)
    @permission_ns.doc(
        responses={
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_200_OK: "SUCCESS",
        }
    )
    def post(self):
        """
        Grants stream permissions to the provided addresses and stream.
        """
        blockchain_name = permission_ns.payload[BLOCKCHAIN_NAME_FIELD_NAME]
        address = permission_ns.payload[ADDRESS_FIELD_NAME]
        stream_name = permission_ns.payload[STREAM_NAME_FIELD_NAME]
        permissions = permission_ns.payload[PERMISSION_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The provided blockchain name can't be empty!")

        if not stream_name or not stream_name.strip():
            raise ValueError("The provided stream name can't be empty!")

        blockchain_name = blockchain_name.strip()
        stream_name = stream_name.strip()
        transaction_id = PermissionController.grant_stream_permission(
            blockchain_name, address, stream_name, permissions
        ).decode("utf-8")
        transaction_id = transaction_id[:-1]
        return {"transactionID": transaction_id}, status.HTTP_200_OK


@permission_ns.route("/revoke_global_permission")
class RevokeGlobalPermission(Resource):
    @permission_ns.expect(global_permission_model, validate=True)
    @permission_ns.doc(
        responses={
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_200_OK: "SUCCESS",
        }
    )
    def post(self):
        """
        Revokes global permissions to the provided addresses.
        """
        blockchain_name = permission_ns.payload[BLOCKCHAIN_NAME_FIELD_NAME]
        addresses = permission_ns.payload[ADDRESSES_FIELD_NAME]
        permissions = permission_ns.payload[PERMISSIONS_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The provided blockchain name can't be empty!")

        blockchain_name = blockchain_name.strip()

        transaction_id = PermissionController.revoke_global_permission(
            blockchain_name, addresses, permissions
        ).decode("utf-8")
        transaction_id = transaction_id[:-1]

        return {"transactionID": transaction_id}, status.HTTP_200_OK


@permission_ns.route("/revoke_stream_permission")
class RevokeStreamPermission(Resource):
    @permission_ns.expect(stream_permission_model, validate=True)
    @permission_ns.doc(
        responses={
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_200_OK: "SUCCESS",
        }
    )
    def post(self):
        """
        Revoke stream permissions to the provided addresses and stream.
        """
        blockchain_name = permission_ns.payload[BLOCKCHAIN_NAME_FIELD_NAME]
        address = permission_ns.payload[ADDRESS_FIELD_NAME]
        stream_name = permission_ns.payload[STREAM_NAME_FIELD_NAME]
        permissions = permission_ns.payload[PERMISSION_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The provided blockchain name can't be empty!")

        if not stream_name or not stream_name.strip():
            raise ValueError("The provided stream name can't be empty!")

        blockchain_name = blockchain_name.strip()
        stream_name = stream_name.strip()

        transaction_id = PermissionController.revoke_stream_permission(
            blockchain_name, address, stream_name, permissions
        ).decode("utf-8")
        transaction_id = transaction_id[:-1]

        return {"transactionID": transaction_id}, status.HTTP_200_OK


get_permission_parser = reqparse.RequestParser(bundle_errors=True)
get_permission_parser.add_argument(
    BLOCKCHAIN_NAME_FIELD_NAME, location="args", type=str, required=True
)
get_permission_parser.add_argument(
    ADDRESSES_FIELD_NAME,
    location="args",
    action="append",
    type=str,
    default=PermissionController.DEFAULT_ADDRESSES_LIST_CONTENT,
)
get_permission_parser.add_argument(
    PERMISSIONS_FIELD_NAME,
    location="args",
    action="append",
    type=str,
    default=PermissionController.DEFAULT_PERMISSIONS_LIST_CONTENT,
)
get_permission_parser.add_argument(
    VERBOSE_FIELD_NAME,
    location="args",
    type=inputs.boolean,
    default=PermissionController.DEFAULT_VERBOSE_VALUE,
)


@permission_ns.route("/get_permissions")
@permission_ns.doc(
    params={
        BLOCKCHAIN_NAME_FIELD_NAME: "blockchain name",
        ADDRESSES_FIELD_NAME: "list of address",
        PERMISSIONS_FIELD_NAME: "list of permissions",
        VERBOSE_FIELD_NAME: "Set verbose to true for additional information about each item’s transaction",
    }
)
class GetPermission(Resource):
    @permission_ns.expect(get_permission_parser)
    @permission_ns.doc(
        responses={
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_200_OK: "SUCCESS",
        }
    )
    def get(self):
        """
        Gets the permissions of the provided addresses, 
        omit permissions to view all permissions, otherwise specific permissions can be passed
        """

        args = get_permission_parser.parse_args(strict=True)

        blockchain_name = args[BLOCKCHAIN_NAME_FIELD_NAME]
        addresses = args[ADDRESSES_FIELD_NAME]
        permissions = args[PERMISSIONS_FIELD_NAME]
        verbose = args[VERBOSE_FIELD_NAME]

        blockchain_name = blockchain_name.strip()

        output = PermissionController.get_permissions(
            blockchain_name, permissions, addresses, verbose
        )

        return {"permissions": output}, status.HTTP_200_OK

