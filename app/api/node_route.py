from flask import Flask, request, jsonify, Blueprint
from flask_api import status
from app.models.node.node_controller import NodeController
from app.models.exception.multichain_error import MultiChainError
import json
from flask_restplus import Namespace, Resource, reqparse, inputs, fields

mod = Blueprint("node", __name__)

NEW_NODE_ADDRESS_FIELD_NAME = "newNodeAddress"
ADMIN_NODE_ADDRESS_FIELD_NAME = "adminNodeAddress"

node_ns = Namespace("node", description="Node API")


admin_node_model = node_ns.model(
    "Admin Node",
    {
        ADMIN_NODE_ADDRESS_FIELD_NAME: fields.String(
            required=True, description="Admin node address"
        )
    },
)


@node_ns.route("/connect_to_admin_node")
class ConnectToAdminNode(Resource):
    @node_ns.expect(admin_node_model, validate=True)
    @node_ns.doc(
        responses={
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_200_OK: "SUCCESS",
        }
    )
    def post(self):
        """
        Connects the current node to the admin node, and returns the wallet address.
        """
        admin_node_address = node_ns.payload[ADMIN_NODE_ADDRESS_FIELD_NAME]

        if not admin_node_address or not admin_node_address.strip():
            raise ValueError("The admin node adddress can't be empty!")

        admin_node_address = admin_node_address.strip()
        wallet_address = NodeController.connect_to_admin_node(admin_node_address)
        return {"walletAddress": wallet_address}, status.HTTP_200_OK


new_node_model = node_ns.model(
    "New Node",
    {
        NEW_NODE_ADDRESS_FIELD_NAME: fields.String(
            required=True, description="New node address"
        )
    },
)


@node_ns.route("/add_node")
class AddNode(Resource):
    @node_ns.expect(new_node_model, validate=True)
    @node_ns.doc(
        responses={
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_200_OK: "SUCCESS",
        }
    )
    def post(self):
        """
        Adds the provided node to the blockchain network
        """
        new_node_address = node_ns.payload[NEW_NODE_ADDRESS_FIELD_NAME]

        if not new_node_address or not new_node_address.strip():
            raise ValueError("The new node adddress can't be empty!")

        new_node_wallet_address = new_node_address.strip()
        return (
            {"walletAddress": NodeController.add_node(new_node_wallet_address)},
            status.HTTP_200_OK,
        )

