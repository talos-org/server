from flask import Flask, request, jsonify, Blueprint
from flask_api import status
from app.models.monitor.network_controller import NetworkController
from app.models.permission.permission_controller import PermissionController
from app.models.exception.multichain_error import MultiChainError
import json
from flask_restplus import Namespace, Resource, reqparse, inputs, fields


BLOCKCHAIN_NAME_FIELD_NAME = "blockchainName"
CONNECTABLE_NODES_FIELD_NAME = "connectableNodes"
VERBOSE = False
ADDRESSES = "*"
PERMISSIONS = ["connect"]

network_ns = Namespace("network", description="Network API")

blockchain_parser = reqparse.RequestParser(bundle_errors=True)
blockchain_parser.add_argument(
    BLOCKCHAIN_NAME_FIELD_NAME, location="args", type=str, required=True
)



@network_ns.route("/get_peer_info")
class PeerInfo(Resource):
    @network_ns.expect(blockchain_parser)
    @network_ns.doc(
        responses={
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_200_OK: "SUCCESS",
        }
    )
    def get(self):
        """
        Returns information relating to all the peers of the node making the request
        """
        args = blockchain_parser.parse_args(strict=True)

        blockchain_name = args[BLOCKCHAIN_NAME_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The blockchain name can't be empty!")

        blockchain_name = blockchain_name.strip()
        peer_info = NetworkController.get_peer_info(blockchain_name)

        return peer_info, status.HTTP_200_OK



@network_ns.route("/get_wallet_address")
class WalletAddress(Resource):
    @network_ns.expect(blockchain_parser)
    @network_ns.doc(
        responses={
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_200_OK: "SUCCESS",
        }
    )
    def get(self):
        """
        Returns the wallet address of the node making the request
        """
        args = blockchain_parser.parse_args(strict=True)

        blockchain_name = args[BLOCKCHAIN_NAME_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The blockchain name can't be empty!")

        blockchain_name = blockchain_name.strip()
        wallet_address = NetworkController.get_wallet_address(blockchain_name)

        return {"walletAddress": wallet_address}, status.HTTP_200_OK
