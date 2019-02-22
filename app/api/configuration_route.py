from flask import Flask, request, jsonify, Blueprint
from flask_api import status
from app.models.configuration.configuration_controller import ConfigurationController
from app.models.exception.multichain_error import MultiChainError
import json
from flask_restplus import Namespace, Resource, reqparse, inputs, fields


BLOCKCHAIN_NAME_FIELD_NAME = "blockchainName"
PARAMETERS_FIELD_NAME = "params"
DESCRIPTION_FIELD_NAME = "description"
MAX_BLOCK_SIZE_FIELD_NAME = "maxBlockSize"
TARGET_BLOCK_TIME = "targetBlockTime"
MINING_TURNOVER = "miningTurnover"


config_ns = Namespace("configuration", description="Configuration API")
cc = ConfigurationController()

blockchain_model = config_ns.model(
    "Blockchain",
    {
        BLOCKCHAIN_NAME_FIELD_NAME: fields.String(
            required=True, description="The blockchain name"
        )
    },
)

blockchain_parser = reqparse.RequestParser(bundle_errors=True)
blockchain_parser.add_argument(
    BLOCKCHAIN_NAME_FIELD_NAME, location="args", type=str, required=True
)


@config_ns.route("/create_chain")
class CreateChain(Resource):
    @config_ns.expect(blockchain_model, validate=True)
    @config_ns.doc(
        responses={
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_200_OK: "SUCCESS",
        }
    )
    def post(self):
        """
        Creates the blockchain with the provided name
        """
        blockchain_name = config_ns.payload[BLOCKCHAIN_NAME_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The blockchain name can't be empty!")

        blockchain_name = blockchain_name.strip()
        cc.create_chain(blockchain_name)
        return ({"status": blockchain_name + " created!"}, status.HTTP_200_OK)


params_model = config_ns.model(
    "Parameters",
    {
        PARAMETERS_FIELD_NAME: fields.String(
            required=True, desription="Blockchain description"
        ),
        MAX_BLOCK_SIZE_FIELD_NAME: fields.Integer(required=True, description=""),
        TARGET_BLOCK_TIME: fields.Integer(required=True, description=""),
        MINING_TURNOVER: fields.Integer(required=True, description=""),
    },
)

config_parameters_model = config_ns.model(
    "Configuation",
    {
        BLOCKCHAIN_NAME_FIELD_NAME: fields.String(
            required=True, description="The blockchain name"
        ),
        PARAMETERS_FIELD_NAME: fields.List(fields.Nested(params_model), required=True),
    },
)


@config_ns.route("/config_parameters")
class ConfigureBlockchain(Resource):
    @config_ns.expect(config_parameters_model, validate=True)
    @config_ns.doc(
        responses={
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_200_OK: "SUCCESS",
        }
    )
    def post(self):
        """
        Configures the parameters in the param.dat using the blockchain name provided
        """

        blockchain_name = config_ns.payload[BLOCKCHAIN_NAME_FIELD_NAME]
        parameters = config_ns.payload[PARAMETERS_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The blockchain name can't be empty!")

        blockchain_name = blockchain_name.strip()

        cc.config_params(blockchain_name, parameters)
        return {"status": "Configurations Changed!"}, status.HTTP_200_OK


@config_ns.route("/deploy_chain")
class DeployChain(Resource):
    @config_ns.expect(blockchain_model, validate=True)
    @config_ns.doc(
        responses={
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_200_OK: "SUCCESS",
        }
    )
    def post(self):
        """
        Deploys the created blockchain
        """
        blockchain_name = config_ns.payload[BLOCKCHAIN_NAME_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The blockchain name can't be empty!")

        blockchain_name = blockchain_name.strip()
        if cc.deploy_blockchain(blockchain_name):
            return ({"status": blockchain_name + " Deployed"}, status.HTTP_200_OK)


@config_ns.route("/get_node_address")
@config_ns.doc(params={BLOCKCHAIN_NAME_FIELD_NAME: "blockchain name"})
class NodeAddress(Resource):
    @config_ns.expect(blockchain_parser)
    @config_ns.doc(
        responses={
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_200_OK: "SUCCESS",
        }
    )
    def get(self):
        """
        Returns the node address of the provided blockchain name
        """
        args = blockchain_parser.parse_args(strict=True)

        blockchain_name = args[BLOCKCHAIN_NAME_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The blockchain name can't be empty!")

        blockchain_name = blockchain_name.strip()

        return (
            {"nodeAddress": cc.get_node_address(blockchain_name)},
            status.HTTP_200_OK,
        )


@config_ns.route("/check_blockchain_name")
@config_ns.doc(params={BLOCKCHAIN_NAME_FIELD_NAME: "blockchain name"})
class BlockchainExist(Resource):
    @config_ns.expect(blockchain_parser)
    @config_ns.doc(
        responses={
            status.HTTP_200_OK: "SUCCESS",
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_409_CONFLICT: "CONFLICT",
        }
    )
    def get(self):
        """
        Determines wheher the blockchain exists or not
        """
        args = blockchain_parser.parse_args(strict=True)

        blockchain_name = args[BLOCKCHAIN_NAME_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The blockchain name can't be empty!")

        blockchain_name = blockchain_name.strip()

        existing_blockchains = cc.get_blockchains()

        if blockchain_name in existing_blockchains:
            blockchain_status = "Blockchain name already exists!"
            
            return {"status": blockchain_status}, status.HTTP_409_CONFLICT
        else:
            blockchain_status = "Valid blockchain name"

            return {"status": blockchain_status}, status.HTTP_200_OK


@config_ns.route("/get_blockchains")
class Blockchain(Resource):
    @config_ns.doc(
        responses={
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_200_OK: "SUCCESS",
        }
    )
    def get(self):
        """
        Returns all the existing blockchains on the requesting node
        """
        existing_blockchains = cc.get_blockchains()

        return ({"blockchains": existing_blockchains}, status.HTTP_200_OK)

