from flask import Flask, request, jsonify, Blueprint
from flask_api import status
from app.models.data.data_controller import DataController
from app.models.exception.multichain_error import MultiChainError
import json
from flask_restplus import Namespace, Resource, reqparse, inputs, fields


VERBOSE_FIELD_NAME = "verbose"
COUNT_FIELD_NAME = "count"
START_FIELD_NAME = "start"
BLOCKCHAIN_NAME_FIELD_NAME = "blockchainName"
STREAM_NAME_FIELD_NAME = "streamName"
DATA_FIELD_NAME = "data"
LOCAL_ORDERING_FIELD_NAME = "localOrdering"
PUBLISHER_FIELD_NAME = "publisher"
PUBLISHERS_FIELD_NAME = "publishers"
KEY_FIELD_NAME = "key"
KEYS_FIELD_NAME = "keys"

data_ns = Namespace("data", description="Data API")


base_parser = reqparse.RequestParser(bundle_errors=True)
base_parser.add_argument(
    BLOCKCHAIN_NAME_FIELD_NAME, location="args", type=str, required=True
)
base_parser.add_argument(
    STREAM_NAME_FIELD_NAME, type=str, location="args", required=True
)
base_parser.add_argument(
    VERBOSE_FIELD_NAME,
    type=inputs.boolean,
    location="args",
    default=DataController.DEFAULT_VERBOSE_VALUE,
)
base_parser.add_argument(
    COUNT_FIELD_NAME,
    type=int,
    location="args",
    default=DataController.DEFAULT_ITEM_COUNT_VALUE,
)
base_parser.add_argument(
    START_FIELD_NAME,
    type=int,
    location="args",
    default=DataController.DEFAULT_ITEM_START_VALUE,
)
base_parser.add_argument(
    LOCAL_ORDERING_FIELD_NAME,
    type=inputs.boolean,
    location="args",
    default=DataController.DEFAULT_LOCAL_ORDERING_VALUE,
)


publish_item_model = data_ns.model(
    "Publish Item",
    {
        BLOCKCHAIN_NAME_FIELD_NAME: fields.String(
            required=True, description="The blockchain name"
        ),
        STREAM_NAME_FIELD_NAME: fields.String(
            required=True, description="The stream name"
        ),
        KEYS_FIELD_NAME: fields.List(
            fields.String, required=True, description="a list of keys for the data"
        ),
        DATA_FIELD_NAME: fields.String(
            required=True, description="the data to be stored"
        ),
    },
)


@data_ns.route("/publish_item")
class PublishItem(Resource):
    @data_ns.expect(publish_item_model, validate=True)
    @data_ns.doc(
        responses={
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_200_OK: "SUCCESS",
        }
    )
    def post(self):
        """
        Publishes an item to a stream.
        """
        blockchain_name = data_ns.payload[BLOCKCHAIN_NAME_FIELD_NAME]
        stream_name = data_ns.payload[STREAM_NAME_FIELD_NAME]
        keys = data_ns.payload[KEYS_FIELD_NAME]
        data = data_ns.payload[DATA_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The blockchain name can't be empty!")

        if not stream_name or not stream_name.strip():
            raise ValueError("The stream name can't be empty!")

        if not keys:
            raise ValueError("The list of keys can't be empty!")

        if not data:
            raise ValueError("The data can't be empty!")

        blockchain_name = blockchain_name.strip()
        stream_name = stream_name.strip()
        
        DataController.publish_item(blockchain_name, stream_name, keys, data)
        return {"status": "Data published!"}, status.HTTP_200_OK


items_keys_parser = base_parser.copy()
items_keys_parser.add_argument(
    KEYS_FIELD_NAME, action="append", location="args", required=True
)
items_keys_parser.remove_argument(START_FIELD_NAME)
items_keys_parser.remove_argument(LOCAL_ORDERING_FIELD_NAME)
items_keys_parser.remove_argument(COUNT_FIELD_NAME)


@data_ns.route("/get_items_by_keys")
@data_ns.doc(
    params={
        BLOCKCHAIN_NAME_FIELD_NAME: "blockchain name",
        STREAM_NAME_FIELD_NAME: "stream name",
        KEYS_FIELD_NAME: "list of keys for the data to be retrieved",
        VERBOSE_FIELD_NAME: "Set verbose to true for additional information about each item’s transaction",
    }
)
class ItemByKey(Resource):
    @data_ns.expect(items_keys_parser)
    @data_ns.doc(
        responses={
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_200_OK: "SUCCESS",
        }
    )
    def get(self):
        """
        Retrieves items in stream which match all of the specified keys in query. 
        """
        args = items_keys_parser.parse_args(strict=True)

        blockchain_name = args[BLOCKCHAIN_NAME_FIELD_NAME]
        stream_name = args[STREAM_NAME_FIELD_NAME]
        keys = args[KEYS_FIELD_NAME]
        verbose = args[VERBOSE_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The blockchain name can't be empty!")

        if not stream_name or not stream_name.strip():
            raise ValueError("The stream name can't be empty!")

        if not keys:
            raise ValueError("The list of keys can't be empty!")

        blockchain_name = blockchain_name.strip()
        stream_name = stream_name.strip()
        json_data = DataController.get_items_by_keys(
            blockchain_name, stream_name, keys, verbose
        )
        return json_data, status.HTTP_200_OK


items_publishers_parser = base_parser.copy()
items_publishers_parser.add_argument(
    PUBLISHERS_FIELD_NAME, action="append", location="args", required=True
)
items_publishers_parser.remove_argument(START_FIELD_NAME)
items_publishers_parser.remove_argument(LOCAL_ORDERING_FIELD_NAME)
items_publishers_parser.remove_argument(COUNT_FIELD_NAME)


@data_ns.route("/get_items_by_publishers")
@data_ns.doc(
    params={
        BLOCKCHAIN_NAME_FIELD_NAME: "blockchain name",
        STREAM_NAME_FIELD_NAME: "stream name",
        PUBLISHERS_FIELD_NAME: "list of publishers wallet address for the data to be retrieved",
        VERBOSE_FIELD_NAME: "Set verbose to true for additional information about each item’s transaction",
    }
)
class ItemByPublisher(Resource):
    @data_ns.expect(items_publishers_parser)
    @data_ns.doc(
        responses={
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_200_OK: "SUCCESS",
        }
    )
    def get(self):
        """
        Retrieves items in stream which match all of the specified publishers in query. 
        """
        args = items_publishers_parser.parse_args(strict=True)

        blockchain_name = args[BLOCKCHAIN_NAME_FIELD_NAME]
        stream_name = args[STREAM_NAME_FIELD_NAME]
        publishers = args[PUBLISHERS_FIELD_NAME]
        verbose = args[VERBOSE_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The blockchain name can't be empty!")

        if not stream_name or not stream_name.strip():
            raise ValueError("The stream name can't be empty!")

        if not publishers:
            raise ValueError("The list of publishers can't be empty!")

        blockchain_name = blockchain_name.strip()
        stream_name = stream_name.strip()
        json_data = DataController.get_items_by_publishers(
            blockchain_name, stream_name, publishers, verbose
        )
        return json_data, status.HTTP_200_OK


@data_ns.route("/get_stream_items")
@data_ns.doc(
    params={
        BLOCKCHAIN_NAME_FIELD_NAME: "blockchain name",
        STREAM_NAME_FIELD_NAME: "stream name",
        VERBOSE_FIELD_NAME: "Set verbose to true for additional information about each item’s transaction",
        COUNT_FIELD_NAME: "retrieve part of the list only ex. only 5 items",
        START_FIELD_NAME: "deals with the ordering of the data retrieved, with negative start values (like the default) indicating the most recent items",
        LOCAL_ORDERING_FIELD_NAME: "Set local-ordering to true to order items by when first seen by this node, rather than their order in the chain",
    }
)
class StreamItem(Resource):
    @data_ns.expect(base_parser)
    @data_ns.doc(
        responses={
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_200_OK: "SUCCESS",
        }
    )
    def get(self):
        """
        Retrieves items in stream. 
        """

        args = base_parser.parse_args(strict=True)

        blockchain_name = args[BLOCKCHAIN_NAME_FIELD_NAME]
        stream_name = args[STREAM_NAME_FIELD_NAME]
        verbose = args[VERBOSE_FIELD_NAME]
        count = args[COUNT_FIELD_NAME]
        start = args[START_FIELD_NAME]
        local_ordering = args[LOCAL_ORDERING_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The blockchain name can't be empty!")

        if not stream_name or not stream_name.strip():
            raise ValueError("The stream name can't be empty!")

        blockchain_name = blockchain_name.strip()
        stream_name = stream_name.strip()
        json_data = DataController.get_stream_items(
            blockchain_name, stream_name, verbose, count, start, local_ordering
        )
        return json_data, status.HTTP_200_OK


stream_publishers_parser = base_parser.copy()
stream_publishers_parser.add_argument(
    PUBLISHERS_FIELD_NAME, action="append", location="args"
)


@data_ns.route("/get_stream_publishers")
@data_ns.doc(
    params={
        BLOCKCHAIN_NAME_FIELD_NAME: "blockchain name",
        STREAM_NAME_FIELD_NAME: "stream name",
        PUBLISHERS_FIELD_NAME: "list of publishers wallet address. This will only return information related to the publishers in the list",
        VERBOSE_FIELD_NAME: "Set verbose to true for additional information about each item’s transaction",
        COUNT_FIELD_NAME: "retrieve part of the list only ex. only 5 items",
        START_FIELD_NAME: "deals with the ordering of the data retrieved, with negative start values (like the default) indicating the most recent items",
        LOCAL_ORDERING_FIELD_NAME: "Set local-ordering to true to order items by when first seen by this node, rather than their order in the chain",
    }
)
class StreamPublisher(Resource):
    @data_ns.expect(stream_publishers_parser)
    @data_ns.doc(
        responses={
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_200_OK: "SUCCESS",
        }
    )
    def get(self):
        """
        Provides information about publishers who have written to a stream
        """
        args = stream_publishers_parser.parse_args(strict=True)

        blockchain_name = args[BLOCKCHAIN_NAME_FIELD_NAME]
        stream_name = args[STREAM_NAME_FIELD_NAME]
        publishers = args[PUBLISHERS_FIELD_NAME]
        verbose = args[VERBOSE_FIELD_NAME]
        count = args[COUNT_FIELD_NAME]
        start = args[START_FIELD_NAME]
        local_ordering = args[LOCAL_ORDERING_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The blockchain name can't be empty!")

        if not stream_name or not stream_name.strip():
            raise ValueError("The stream name can't be empty!")

        blockchain_name = blockchain_name.strip()
        stream_name = stream_name.strip()
        json_data = DataController.get_stream_publishers(
            blockchain_name,
            stream_name,
            publishers,
            verbose,
            count,
            start,
            local_ordering,
        )
        return json_data, status.HTTP_200_OK


stream_keys_parser = base_parser.copy()
stream_keys_parser.add_argument(KEYS_FIELD_NAME, action="append", location="args")


@data_ns.route("/get_stream_keys")
@data_ns.doc(
    params={
        BLOCKCHAIN_NAME_FIELD_NAME: "blockchain name",
        STREAM_NAME_FIELD_NAME: "stream name",
        KEYS_FIELD_NAME: "list of keys that belong to the stream. This will only return information related to the keys in the list",
        VERBOSE_FIELD_NAME: "Set verbose to true for additional information about each item’s transaction",
        COUNT_FIELD_NAME: "retrieve part of the list only ex. only 5 items",
        START_FIELD_NAME: "deals with the ordering of the data retrieved, with negative start values (like the default) indicating the most recent items",
        LOCAL_ORDERING_FIELD_NAME: "Set local-ordering to true to order items by when first seen by this node, rather than their order in the chain",
    }
)
class StreamKey(Resource):
    @data_ns.expect(stream_keys_parser)
    @data_ns.doc(
        responses={
            status.HTTP_400_BAD_REQUEST: "BAD REQUEST",
            status.HTTP_200_OK: "SUCCESS",
        }
    )
    def get(self):
        """
        Provides information about keys in a stream
        """
        args = stream_keys_parser.parse_args(strict=True)

        blockchain_name = args[BLOCKCHAIN_NAME_FIELD_NAME]
        stream_name = args[STREAM_NAME_FIELD_NAME]
        stream_keys = args[KEYS_FIELD_NAME]
        verbose = args[VERBOSE_FIELD_NAME]
        count = args[COUNT_FIELD_NAME]
        start = args[START_FIELD_NAME]
        local_ordering = args[LOCAL_ORDERING_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The blockchain name can't be empty!")

        if not stream_name or not stream_name.strip():
            raise ValueError("The stream name can't be empty!")

        blockchain_name = blockchain_name.strip()
        stream_name = stream_name.strip()
        json_data = DataController.get_stream_keys(
            blockchain_name,
            stream_name,
            stream_keys,
            verbose,
            count,
            start,
            local_ordering,
        )
        return json_data, status.HTTP_200_OK
