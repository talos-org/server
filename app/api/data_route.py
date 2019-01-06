from flask import Flask, request, jsonify, Blueprint
from flask_api import status
from app.models.data.data_controller import DataController
from app.models.exception.multichain_error import MultiChainError
import json


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

mod = Blueprint("data", __name__)


def convert_to_boolean(field_name: str, value: str):
    try:
        if value in ["True", "true"]:
            return True
        elif value in ["False", "false"]:
            return False
        raise ValueError(
            "The value provided for " + field_name + " is not a valid boolean value"
        )
    except ValueError as ex:
        raise ex
    except Exception as ex:
        raise ex


def convert_to_int(field_name: str, value: str):
    try:
        return int(value)
    except ValueError as ex:
        raise ValueError("The value provided for " + field_name + " is not an integer")
    except Exception as ex:
        raise ex


"""
Publishes an item to a stream
The following data is expected in the body of the request:
    "blockchainName": blockchain name
    "streamName": stream name
    "keys": a list of keys for the data
    "data": the data to be stored 
"""


@mod.route("/publish_item/", methods=["POST"])
def publish_item():
    try:
        json_request = request.get_json()

        if not json_request:
            return (
                jsonify({"error": "The request body is empty!"}),
                status.HTTP_204_NO_CONTENT,
            )

        blockchain_name = json_request[BLOCKCHAIN_NAME_FIELD_NAME]
        stream_name = json_request[STREAM_NAME_FIELD_NAME]
        keys = json_request[KEYS_FIELD_NAME]
        data = json_request[DATA_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            return (
                jsonify({"error": "The blockchain name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not stream_name or not stream_name.strip():
            return (
                jsonify({"error": "The stream name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not keys:
            return (
                jsonify({"error": "The list of keys can't be empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not data:
            return (
                jsonify({"error": "The data can't be empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        blockchain_name = blockchain_name.strip()
        stream_name = stream_name.strip()
        json_data = json.dumps(data)
        DataController.publish_item(blockchain_name, stream_name, keys, json_data)
        return jsonify({"Status": "Data published!"}), status.HTTP_200_OK
    except ValueError as ex:
        return (
            jsonify({"error": "The data is not a valid JSON"}),
            status.HTTP_400_BAD_REQUEST,
        )
    except MultiChainError as ex:
        return jsonify(ex.get_info()), status.HTTP_400_BAD_REQUEST
    except Exception as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST


"""
Retrieves items that belong to the specified key from stream, passed as a stream name to 
which the node must be subscribed.
The following data is expected in the body of the request:
    "blockchainName": blockchain name
    "streamName": stream name
    "key": key for the data to be retrieved
    OPTIONAL: "verbose": Set verbose to true for additional information about each item’s transaction
    OPTIONAL: "count": retrieve part of the list only ex. only 5 items
    OPTIONAL: "start": deals with the ordering of the data retrieved, with negative start values (like the default) indicating the most recent items
    OPTIONAL: "localOrdering": Set local-ordering to true to order items by when first seen by this node, rather than their order in the chain
"""


@mod.route("/get_items_by_key/", methods=["GET"])
def get_items_by_key():
    try:
        json_request = request.get_json()

        if not json_request:
            return (
                jsonify({"error": "The request body is empty!"}),
                status.HTTP_204_NO_CONTENT,
            )

        blockchain_name = json_request[BLOCKCHAIN_NAME_FIELD_NAME]
        stream_name = json_request[STREAM_NAME_FIELD_NAME]
        key = json_request[KEY_FIELD_NAME]
        verbose = DataController.DEFAULT_VERBOSE_VALUE
        count = DataController.DEFAULT_ITEM_COUNT_VALUE
        start = DataController.DEFAULT_ITEM_START_VALUE
        local_ordering = DataController.DEFAULT_LOCAL_ORDERING_VALUE

        if not blockchain_name or not blockchain_name.strip():
            return (
                jsonify({"error": "The blockchain name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not stream_name or not stream_name.strip():
            return (
                jsonify({"error": "The stream name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not key or not key.strip():
            return (
                jsonify({"error": "The data key can't be empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if VERBOSE_FIELD_NAME in json_request:
            verbose = convert_to_boolean(
                VERBOSE_FIELD_NAME, json_request[VERBOSE_FIELD_NAME]
            )

        if COUNT_FIELD_NAME in json_request:
            count = convert_to_int(COUNT_FIELD_NAME, json_request[COUNT_FIELD_NAME])

        if START_FIELD_NAME in json_request:
            start = convert_to_int(START_FIELD_NAME, json_request[START_FIELD_NAME])

        if LOCAL_ORDERING_FIELD_NAME in json_request:
            local_ordering = convert_to_int(
                LOCAL_ORDERING_FIELD_NAME, json_request[LOCAL_ORDERING_FIELD_NAME]
            )

        blockchain_name = blockchain_name.strip()
        stream_name = stream_name.strip()
        key = key.strip()
        json_data = DataController.get_items_by_key(
            blockchain_name, stream_name, key, verbose, count, start, local_ordering
        )
        return jsonify({"Data": json_data}), status.HTTP_200_OK
    except ValueError as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST
    except Exception as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST


"""
Retrieves items in stream which match all of the specified keys in query. 
The keys field should specify an array of keys.
The following data is expected in the body of the request:
    "blockchainName": blockchain name
    "streamName": stream name
    "keys": list of keys for the data to be retrieved
    OPTIONAL: "verbose": Set verbose to true for additional information about each item’s transaction
"""


@mod.route("/get_items_by_keys/", methods=["GET"])
def get_items_by_keys():
    try:
        json_request = request.get_json()

        if not json_request:
            return (
                jsonify({"error": "The request body is empty!"}),
                status.HTTP_204_NO_CONTENT,
            )

        blockchain_name = json_request[BLOCKCHAIN_NAME_FIELD_NAME]
        stream_name = json_request[STREAM_NAME_FIELD_NAME]
        keys = json_request[KEYS_FIELD_NAME]
        verbose = DataController.DEFAULT_VERBOSE_VALUE

        if not blockchain_name or not blockchain_name.strip():
            return (
                jsonify({"error": "The blockchain name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not stream_name or not stream_name.strip():
            return (
                jsonify({"error": "The stream name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not keys:
            return (
                jsonify({"error": "The list of keys can't be empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if VERBOSE_FIELD_NAME in json_request:
            verbose = convert_to_boolean(
                VERBOSE_FIELD_NAME, json_request[VERBOSE_FIELD_NAME]
            )

        blockchain_name = blockchain_name.strip()
        stream_name = stream_name.strip()
        json_data = DataController.get_items_by_keys(
            blockchain_name, stream_name, keys, verbose
        )
        return jsonify({"Data": json_data}), status.HTTP_200_OK
    except ValueError as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST
    except Exception as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST


"""
Retrieves items that belong to the specified publisher from stream.
The following data is expected in the body of the request:
    "blockchainName": blockchain name
    "streamName": stream name
    "publisher": Wallet address of the items publisher
    OPTIONAL: "verbose": Set verbose to true for additional information about each item’s transaction
    OPTIONAL: "count": retrieve part of the list only ex. only 5 items
    OPTIONAL: "start": deals with the ordering of the data retrieved, with negative start values (like the default) indicating the most recent items
    OPTIONAL: "localOrdering": Set local-ordering to true to order items by when first seen by this node, rather than their order in the chain
"""


@mod.route("/get_items_by_publisher/", methods=["GET"])
def get_items_by_publisher():
    try:
        json_request = request.get_json()

        if not json_request:
            return (
                jsonify({"error": "The request body is empty!"}),
                status.HTTP_204_NO_CONTENT,
            )

        blockchain_name = json_request[BLOCKCHAIN_NAME_FIELD_NAME]
        stream_name = json_request[STREAM_NAME_FIELD_NAME]
        publisher = json_request[PUBLISHER_FIELD_NAME]
        verbose = DataController.DEFAULT_VERBOSE_VALUE
        count = DataController.DEFAULT_ITEM_COUNT_VALUE
        start = DataController.DEFAULT_ITEM_START_VALUE
        local_ordering = DataController.DEFAULT_LOCAL_ORDERING_VALUE

        if not blockchain_name or not blockchain_name.strip():
            return (
                jsonify({"error": "The blockchain name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not stream_name or not stream_name.strip():
            return (
                jsonify({"error": "The stream name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not publisher or not publisher.strip():
            return (
                jsonify({"error": "The publisher wallet address can't be empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if VERBOSE_FIELD_NAME in json_request:
            verbose = convert_to_boolean(
                VERBOSE_FIELD_NAME, json_request[VERBOSE_FIELD_NAME]
            )

        if COUNT_FIELD_NAME in json_request:
            count = convert_to_int(COUNT_FIELD_NAME, json_request[COUNT_FIELD_NAME])

        if START_FIELD_NAME in json_request:
            start = convert_to_int(START_FIELD_NAME, json_request[START_FIELD_NAME])

        if LOCAL_ORDERING_FIELD_NAME in json_request:
            local_ordering = convert_to_int(
                LOCAL_ORDERING_FIELD_NAME, json_request[LOCAL_ORDERING_FIELD_NAME]
            )

        blockchain_name = blockchain_name.strip()
        stream_name = stream_name.strip()
        publisher = publisher.strip()
        json_data = DataController.get_items_by_publisher(
            blockchain_name,
            stream_name,
            publisher,
            verbose,
            count,
            start,
            local_ordering,
        )
        return jsonify({"Data": json_data}), status.HTTP_200_OK
    except ValueError as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST
    except Exception as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST


"""
Retrieves items in stream which match all of the specified publishers in query. 
The publishers field should specify an array of publishers.
The following data is expected in the body of the request:
    "blockchainName": blockchain name
    "streamName": stream name
    "publishers": list of publishers wallet address for the data to be retrieved
    OPTIONAL: "verbose": Set verbose to true for additional information about each item’s transaction
"""


@mod.route("/get_items_by_publishers/", methods=["GET"])
def get_items_by_publishers():
    try:
        json_request = request.get_json()

        if not json_request:
            return (
                jsonify({"error": "The request body is empty!"}),
                status.HTTP_204_NO_CONTENT,
            )

        blockchain_name = json_request[BLOCKCHAIN_NAME_FIELD_NAME]
        stream_name = json_request[STREAM_NAME_FIELD_NAME]
        publishers = json_request[PUBLISHERS_FIELD_NAME]
        verbose = DataController.DEFAULT_VERBOSE_VALUE

        if not blockchain_name or not blockchain_name.strip():
            return (
                jsonify({"error": "The blockchain name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not stream_name or not stream_name.strip():
            return (
                jsonify({"error": "The stream name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not publishers:
            return (
                jsonify({"error": "The list of publishers can't be empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if VERBOSE_FIELD_NAME in json_request:
            verbose = convert_to_boolean(
                VERBOSE_FIELD_NAME, json_request[VERBOSE_FIELD_NAME]
            )

        blockchain_name = blockchain_name.strip()
        stream_name = stream_name.strip()
        json_data = DataController.get_items_by_publishers(
            blockchain_name, stream_name, publishers, verbose
        )
        return jsonify({"Data": json_data}), status.HTTP_200_OK
    except ValueError as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST
    except Exception as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST


"""
Retrieves items in stream. 
The following data is expected in the body of the request:
    "blockchainName": blockchain name
    "streamName": stream name
    OPTIONAL: "verbose": Set verbose to true for additional information about each item’s transaction
    OPTIONAL: "count": retrieve part of the list only ex. only 5 items
    OPTIONAL: "start": deals with the ordering of the data retrieved, with negative start values (like the default) indicating the most recent items
    OPTIONAL: "localOrdering": Set local-ordering to true to order items by when first seen by this node, rather than their order in the chain
"""


@mod.route("/get_stream_items/", methods=["GET"])
def get_stream_items():
    try:
        json_request = request.get_json()

        if not json_request:
            return (
                jsonify({"error": "The request body is empty!"}),
                status.HTTP_204_NO_CONTENT,
            )

        blockchain_name = json_request[BLOCKCHAIN_NAME_FIELD_NAME]
        stream_name = json_request[STREAM_NAME_FIELD_NAME]
        verbose = DataController.DEFAULT_VERBOSE_VALUE
        count = DataController.DEFAULT_ITEM_COUNT_VALUE
        start = DataController.DEFAULT_ITEM_START_VALUE
        local_ordering = DataController.DEFAULT_LOCAL_ORDERING_VALUE

        if not blockchain_name or not blockchain_name.strip():
            return (
                jsonify({"error": "The blockchain name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not stream_name or not stream_name.strip():
            return (
                jsonify({"error": "The stream name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if VERBOSE_FIELD_NAME in json_request:
            verbose = convert_to_boolean(
                VERBOSE_FIELD_NAME, json_request[VERBOSE_FIELD_NAME]
            )

        if COUNT_FIELD_NAME in json_request:
            count = convert_to_int(COUNT_FIELD_NAME, json_request[COUNT_FIELD_NAME])

        if START_FIELD_NAME in json_request:
            start = convert_to_int(START_FIELD_NAME, json_request[START_FIELD_NAME])

        if LOCAL_ORDERING_FIELD_NAME in json_request:
            local_ordering = convert_to_int(
                LOCAL_ORDERING_FIELD_NAME, json_request[LOCAL_ORDERING_FIELD_NAME]
            )

        blockchain_name = blockchain_name.strip()
        stream_name = stream_name.strip()
        json_data = DataController.get_stream_items(
            blockchain_name, stream_name, verbose, count, start, local_ordering
        )
        return jsonify({"Data": json_data}), status.HTTP_200_OK
    except ValueError as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST
    except Exception as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST


"""
Provides information about publishers who have written to a stream
The following data is expected in the body of the request:
    "blockchainName": blockchain name
    "streamName": stream name
    OPTIONAL: "publishers": list of publishers wallet address. This will cause the function to only return information related to the publishers in the list
    OPTIONAL: "verbose": Set verbose to true for additional information about each item’s transaction
    OPTIONAL: "count": retrieve part of the list only ex. only 5 items
    OPTIONAL: "start": deals with the ordering of the data retrieved, with negative start values (like the default) indicating the most recent items
    OPTIONAL: "localOrdering": Set local-ordering to true to order items by when first seen by this node, rather than their order in the chain
"""


@mod.route("/get_stream_publishers/", methods=["GET"])
def get_stream_publishers():
    try:
        json_request = request.get_json()

        if not json_request:
            return (
                jsonify({"error": "The request body is empty!"}),
                status.HTTP_204_NO_CONTENT,
            )

        blockchain_name = json_request[BLOCKCHAIN_NAME_FIELD_NAME]
        stream_name = json_request[STREAM_NAME_FIELD_NAME]
        publishers = DataController.DEFAULT_PUBLISHERS_LIST_CONTENT
        verbose = DataController.DEFAULT_VERBOSE_VALUE
        count = DataController.DEFAULT_ITEM_COUNT_VALUE
        start = DataController.DEFAULT_ITEM_START_VALUE
        local_ordering = DataController.DEFAULT_LOCAL_ORDERING_VALUE

        if not blockchain_name or not blockchain_name.strip():
            return (
                jsonify({"error": "The blockchain name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not stream_name or not stream_name.strip():
            return (
                jsonify({"error": "The stream name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if PUBLISHERS_FIELD_NAME in json_request:
            publishers = json_request[PUBLISHERS_FIELD_NAME]
            if not publishers:
                return (
                    jsonify({"error": "The list of publishers can't be empty!"}),
                    status.HTTP_400_BAD_REQUEST,
                )

        if VERBOSE_FIELD_NAME in json_request:
            verbose = convert_to_boolean(
                VERBOSE_FIELD_NAME, json_request[VERBOSE_FIELD_NAME]
            )

        if COUNT_FIELD_NAME in json_request:
            count = convert_to_int(COUNT_FIELD_NAME, json_request[COUNT_FIELD_NAME])

        if START_FIELD_NAME in json_request:
            start = convert_to_int(START_FIELD_NAME, json_request[START_FIELD_NAME])

        if LOCAL_ORDERING_FIELD_NAME in json_request:
            local_ordering = convert_to_int(
                LOCAL_ORDERING_FIELD_NAME, json_request[LOCAL_ORDERING_FIELD_NAME]
            )

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
        return jsonify({"Data": json_data}), status.HTTP_200_OK
    except ValueError as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST
    except Exception as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST

