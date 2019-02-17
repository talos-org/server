from flask import Flask, request, jsonify, Blueprint
from flask_api import status
from app.models.data.data_stream_controller import DataStreamController
from app.models.exception.multichain_error import MultiChainError
import json
from flask_restplus import Namespace, Resource, reqparse, inputs, fields

VERBOSE_FIELD_NAME = "verbose"
COUNT_FIELD_NAME = "count"
START_FIELD_NAME = "start"
BLOCKCHAIN_NAME_FIELD_NAME = "blockchainName"
STREAM_NAME_FIELD_NAME = "streamName"
IS_OPEN_FIELD_NAME = "isOpen"
STREAMS_FIELD_NAME = "streams"
RESCAN_FIELD_NAME = "rescan"

data_stream_ns = Namespace("data_streams", description="Data Streams API")

create_stream_model = data_stream_ns.model(
    "Create Stream",
    {
        BLOCKCHAIN_NAME_FIELD_NAME: fields.String(
            required=True, description="The blockchain name"
        ),
        STREAM_NAME_FIELD_NAME: fields.String(
            required=True, description="The stream name"
        ),
        IS_OPEN_FIELD_NAME: fields.Boolean(
            required=True,
            description="If open is true then anyone with global send permissions can publish to the stream, otherwise publishers must be explicitly granted per-stream write permissions",
        ),
    },
)


@data_stream_ns.route("/create_stream")
class CreateStream(Resource):
    @data_stream_ns.expect(create_stream_model, validate=True)
    @data_stream_ns.doc(
        responses={
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_200_OK: "SUCCESS",
        }
    )
    def post(self):
        """
        Creates a new stream on the blockchain.
        """
        blockchain_name = data_stream_ns.payload[BLOCKCHAIN_NAME_FIELD_NAME]
        stream_name = data_stream_ns.payload[STREAM_NAME_FIELD_NAME]
        is_open = data_stream_ns.payload[IS_OPEN_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The blockchain name can't be empty!")

        if not stream_name or not stream_name.strip():
            raise ValueError("The stream name can't be empty!")

        blockchain_name = blockchain_name.strip()
        stream_name = stream_name.strip()
        DataStreamController.create_stream(blockchain_name, stream_name, is_open)
        return {"status": stream_name + " created!"}, status.HTTP_200_OK


get_stream_parser = reqparse.RequestParser(bundle_errors=True)
get_stream_parser.add_argument(
    BLOCKCHAIN_NAME_FIELD_NAME, location="args", type=str, required=True
)
get_stream_parser.add_argument(
    STREAMS_FIELD_NAME,
    location="args",
    action="append",
    type=str,
    default=DataStreamController.DEFAULT_STREAMS_LIST_CONTENT,
)
get_stream_parser.add_argument(
    VERBOSE_FIELD_NAME,
    location="args",
    type=inputs.boolean,
    default=DataStreamController.DEFAULT_VERBOSE_VALUE,
)
get_stream_parser.add_argument(
    COUNT_FIELD_NAME,
    location="args",
    type=int,
    default=DataStreamController.DEFAULT_STREAM_COUNT_VALUE,
)
get_stream_parser.add_argument(
    START_FIELD_NAME,
    location="args",
    type=int,
    default=DataStreamController.DEFAULT_STREAM_START_VALUE,
)


@data_stream_ns.route("/get_streams")
@data_stream_ns.doc(
    params={
        BLOCKCHAIN_NAME_FIELD_NAME: "blockchain name",
        STREAMS_FIELD_NAME: "stream names",
        VERBOSE_FIELD_NAME: "Set verbose to true for additional information about each item’s transaction",
        COUNT_FIELD_NAME: "retrieve part of the list only ex. only 5 items",
        START_FIELD_NAME: "deals with the ordering of the data retrieved, with negative start values (like the default) indicating the most recent items",
    }
)
class GetStream(Resource):
    @data_stream_ns.expect(get_stream_parser)
    @data_stream_ns.doc(
        responses={
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_200_OK: "SUCCESS",
        }
    )
    def get(self):
        """
        Returns information about streams created on the blockchain
        """

        args = get_stream_parser.parse_args(strict=True)

        blockchain_name = args[BLOCKCHAIN_NAME_FIELD_NAME]
        streams = args[STREAMS_FIELD_NAME]
        verbose = args[VERBOSE_FIELD_NAME]
        count = args[COUNT_FIELD_NAME]
        start = args[START_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The blockchain name can't be empty!")

        blockchain_name = blockchain_name.strip()
        json_data = DataStreamController.get_streams(
            blockchain_name, streams, verbose, count, start
        )
        return json_data, status.HTTP_200_OK


subscribe_stream_model = data_stream_ns.model(
    "Subscribe Stream",
    {
        BLOCKCHAIN_NAME_FIELD_NAME: fields.String(
            required=True, description="The blockchain name"
        ),
        STREAMS_FIELD_NAME: fields.List(
            fields.String, required=True, description="list of streams to subscribe to"
        ),
        RESCAN_FIELD_NAME: fields.Boolean(
            default=DataStreamController.DEFAULT_RESCAN_VALUE,
            description="Set rescan to true to cause the node to reindex all items from when the streams were created, as well as those in other subscribed entities",
        ),
    },
)


@data_stream_ns.route("/subscribe")
class SubscribeStream(Resource):
    @data_stream_ns.expect(subscribe_stream_model, validate=True)
    @data_stream_ns.doc(
        responses={
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_200_OK: "SUCCESS",
        }
    )
    def post(self):
        """
        Instructs the node to start tracking one or more stream(s).
        """
        blockchain_name = data_stream_ns.payload[BLOCKCHAIN_NAME_FIELD_NAME]
        streams = data_stream_ns.payload[STREAMS_FIELD_NAME]
        rescan = data_stream_ns.payload[RESCAN_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The blockchain name can't be empty!")

        if not streams:
            raise ValueError("The list of streams can't be empty!")

        blockchain_name = blockchain_name.strip()
        result = DataStreamController.subscribe(blockchain_name, streams, rescan)
        if result:
            return {"status": "Subscribed successfully!"}, status.HTTP_200_OK
        return (
            {"status": "Failed to subscribe to stream(s)"},
            status.HTTP_400_BAD_REQUEST,
        )


unsubscribe_stream_model = data_stream_ns.model(
    "Unsubscribe Stream",
    {
        BLOCKCHAIN_NAME_FIELD_NAME: fields.String(
            required=True, description="The blockchain name"
        ),
        STREAMS_FIELD_NAME: fields.List(
            fields.String,
            required=True,
            description="list of streams to unsubscribe from",
        ),
    },
)


@data_stream_ns.route("/unsubscribe")
class UnsubscribeStream(Resource):
    @data_stream_ns.expect(unsubscribe_stream_model, validate=True)
    @data_stream_ns.doc(
        responses={
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_200_OK: "SUCCESS",
        }
    )
    def post(self):
        """
        Instructs the node to stop tracking one or more stream(s)
        """

        blockchain_name = data_stream_ns.payload[BLOCKCHAIN_NAME_FIELD_NAME]
        streams = data_stream_ns.payload[STREAMS_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The blockchain name can't be empty!")

        if not streams:
            raise ValueError("The list of streams can't be empty!")

        blockchain_name = blockchain_name.strip()
        result = DataStreamController.unsubscribe(blockchain_name, streams)
        if result:
            return {"status": "Unsubscribed successfully!"}, status.HTTP_200_OK
        return (
            {"status": "Failed to unsubscribe from stream(s)"},
            status.HTTP_400_BAD_REQUEST,
        )
