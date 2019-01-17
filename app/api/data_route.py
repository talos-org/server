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
PUBLISHERS_PARAMETER_NAME = PUBLISHERS_FIELD_NAME + "[]"
KEY_FIELD_NAME = "key"
KEYS_FIELD_NAME = "keys"
KEYS_PARAMETER_NAME = KEYS_FIELD_NAME + "[]"

mod = Blueprint("data", __name__)


def convert_to_boolean(field_name: str, value: str):
    try:
        if value in ["True", "true", True]:
            return True
        elif value in ["False", "false", False]:
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


@mod.route("/publish_item", methods=["POST"])
def publish_item():
    try:
        json_request = request.get_json()

        if not json_request:
            return (
                jsonify({"error": "The request body is empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not BLOCKCHAIN_NAME_FIELD_NAME in json_request:
            return (
                jsonify(
                    {
                        "error": "The "
                        + BLOCKCHAIN_NAME_FIELD_NAME
                        + " field was not found in the request!"
                    }
                ),
                status.HTTP_400_BAD_REQUEST,
            )

        if not STREAM_NAME_FIELD_NAME in json_request:
            return (
                jsonify(
                    {
                        "error": "The "
                        + STREAM_NAME_FIELD_NAME
                        + " field was not found in the request!"
                    }
                ),
                status.HTTP_400_BAD_REQUEST,
            )

        if not KEYS_FIELD_NAME in json_request:
            return (
                jsonify(
                    {
                        "error": "The "
                        + KEYS_FIELD_NAME
                        + " field was not found in the request!"
                    }
                ),
                status.HTTP_400_BAD_REQUEST,
            )

        if not DATA_FIELD_NAME in json_request:
            return (
                jsonify(
                    {
                        "error": "The "
                        + DATA_FIELD_NAME
                        + " field was not found in the request!"
                    }
                ),
                status.HTTP_400_BAD_REQUEST,
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

        if not isinstance(keys, list):
            return (
                jsonify({"error": "You must pass a list of keys"}),
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
The following data is expected to be passed in as query parameters:
    "blockchainName": blockchain name
    "streamName": stream name
    "key": key for the data to be retrieved
    OPTIONAL: "verbose": Set verbose to true for additional information about each item’s transaction
    OPTIONAL: "count": retrieve part of the list only ex. only 5 items
    OPTIONAL: "start": deals with the ordering of the data retrieved, with negative start values (like the default) indicating the most recent items
    OPTIONAL: "localOrdering": Set local-ordering to true to order items by when first seen by this node, rather than their order in the chain
"""


@mod.route("/get_items_by_key", methods=["GET"])
def get_items_by_key():
    try:
        request_args = request.args

        if not request_args:
            return (
                jsonify({"error": "No parameters were passed!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        blockchain_name = request_args.get(BLOCKCHAIN_NAME_FIELD_NAME)
        stream_name = request_args.get(STREAM_NAME_FIELD_NAME)
        key = request_args.get(KEY_FIELD_NAME)

        if blockchain_name is None:
            return (
                jsonify(
                    {
                        "error": "The "
                        + BLOCKCHAIN_NAME_FIELD_NAME
                        + " parameter was not found in the request!"
                    }
                ),
                status.HTTP_400_BAD_REQUEST,
            )

        if stream_name is None:
            return (
                jsonify(
                    {
                        "error": "The "
                        + STREAM_NAME_FIELD_NAME
                        + " parameter was not found in the request!"
                    }
                ),
                status.HTTP_400_BAD_REQUEST,
            )

        if key is None:
            return (
                jsonify(
                    {
                        "error": "The "
                        + KEY_FIELD_NAME
                        + " parameter was not found in the request!"
                    }
                ),
                status.HTTP_400_BAD_REQUEST,
            )

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

        if not request_args.get(VERBOSE_FIELD_NAME) is None:
            verbose = convert_to_boolean(
                VERBOSE_FIELD_NAME, request_args.get(VERBOSE_FIELD_NAME)
            )

        if not request_args.get(COUNT_FIELD_NAME) is None:
            count = convert_to_int(COUNT_FIELD_NAME, request_args.get(COUNT_FIELD_NAME))

        if not request_args.get(START_FIELD_NAME) is None:
            start = convert_to_int(START_FIELD_NAME, request_args.get(START_FIELD_NAME))

        if not request_args.get(LOCAL_ORDERING_FIELD_NAME) is None:
            local_ordering = convert_to_int(
                LOCAL_ORDERING_FIELD_NAME, request_args.get(LOCAL_ORDERING_FIELD_NAME)
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
The following data is expected to be passed in as query parameters:
    "blockchainName": blockchain name
    "streamName": stream name
    "keys": list of keys for the data to be retrieved
    OPTIONAL: "verbose": Set verbose to true for additional information about each item’s transaction
"""


@mod.route("/get_items_by_keys", methods=["GET"])
def get_items_by_keys():
    try:
        request_args = request.args

        if not request_args:
            return (
                jsonify({"error": "No parameters were passed!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        blockchain_name = request_args.get(BLOCKCHAIN_NAME_FIELD_NAME)
        stream_name = request_args.get(STREAM_NAME_FIELD_NAME)
        keys = request_args.getlist(KEYS_PARAMETER_NAME)
        verbose = DataController.DEFAULT_VERBOSE_VALUE

        if blockchain_name is None:
            return (
                jsonify(
                    {
                        "error": "The "
                        + BLOCKCHAIN_NAME_FIELD_NAME
                        + " parameter was not found in the request!"
                    }
                ),
                status.HTTP_400_BAD_REQUEST,
            )

        if stream_name is None:
            return (
                jsonify(
                    {
                        "error": "The "
                        + STREAM_NAME_FIELD_NAME
                        + " parameter was not found in the request!"
                    }
                ),
                status.HTTP_400_BAD_REQUEST,
            )

        if not keys:
            return (
                jsonify(
                    {
                        "error": "The "
                        + KEYS_PARAMETER_NAME
                        + " parameter was not found in the request!"
                    }
                ),
                status.HTTP_400_BAD_REQUEST,
            )

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

        if not isinstance(keys, list):
            return (
                jsonify({"error": "You must pass a list of keys"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not request_args.get(VERBOSE_FIELD_NAME) is None:
            verbose = convert_to_boolean(
                VERBOSE_FIELD_NAME, request_args.get(VERBOSE_FIELD_NAME)
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
The following data is expected to be passed in as query parameters:
    "blockchainName": blockchain name
    "streamName": stream name
    "publisher": Wallet address of the items publisher
    OPTIONAL: "verbose": Set verbose to true for additional information about each item’s transaction
    OPTIONAL: "count": retrieve part of the list only ex. only 5 items
    OPTIONAL: "start": deals with the ordering of the data retrieved, with negative start values (like the default) indicating the most recent items
    OPTIONAL: "localOrdering": Set local-ordering to true to order items by when first seen by this node, rather than their order in the chain
"""


@mod.route("/get_items_by_publisher", methods=["GET"])
def get_items_by_publisher():
    try:
        request_args = request.args

        if not request_args:
            return (
                jsonify({"error": "No parameters were passed!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        blockchain_name = request_args.get(BLOCKCHAIN_NAME_FIELD_NAME)
        stream_name = request_args.get(STREAM_NAME_FIELD_NAME)
        publisher = request_args.get(PUBLISHER_FIELD_NAME)
        verbose = DataController.DEFAULT_VERBOSE_VALUE
        count = DataController.DEFAULT_ITEM_COUNT_VALUE
        start = DataController.DEFAULT_ITEM_START_VALUE
        local_ordering = DataController.DEFAULT_LOCAL_ORDERING_VALUE

        if blockchain_name is None:
            return (
                jsonify(
                    {
                        "error": "The "
                        + BLOCKCHAIN_NAME_FIELD_NAME
                        + " parameter was not found in the request!"
                    }
                ),
                status.HTTP_400_BAD_REQUEST,
            )

        if stream_name is None:
            return (
                jsonify(
                    {
                        "error": "The "
                        + STREAM_NAME_FIELD_NAME
                        + " parameter was not found in the request!"
                    }
                ),
                status.HTTP_400_BAD_REQUEST,
            )

        if publisher is None:
            return (
                jsonify(
                    {
                        "error": "The "
                        + PUBLISHER_FIELD_NAME
                        + " parameter was not found in the request!"
                    }
                ),
                status.HTTP_400_BAD_REQUEST,
            )

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

        if not request_args.get(VERBOSE_FIELD_NAME) is None:
            verbose = convert_to_boolean(
                VERBOSE_FIELD_NAME, request_args.get(VERBOSE_FIELD_NAME)
            )

        if not request_args.get(COUNT_FIELD_NAME) is None:
            count = convert_to_int(COUNT_FIELD_NAME, request_args.get(COUNT_FIELD_NAME))

        if not request_args.get(START_FIELD_NAME) is None:
            start = convert_to_int(START_FIELD_NAME, request_args.get(START_FIELD_NAME))

        if not request_args.get(LOCAL_ORDERING_FIELD_NAME) is None:
            local_ordering = convert_to_int(
                LOCAL_ORDERING_FIELD_NAME, request_args.get(LOCAL_ORDERING_FIELD_NAME)
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
The following data is expected to be passed in as query parameters:
    "blockchainName": blockchain name
    "streamName": stream name
    "publishers": list of publishers wallet address for the data to be retrieved
    OPTIONAL: "verbose": Set verbose to true for additional information about each item’s transaction
"""


@mod.route("/get_items_by_publishers", methods=["GET"])
def get_items_by_publishers():
    try:
        request_args = request.args

        if not request_args:
            return (
                jsonify({"error": "No parameters were passed!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        blockchain_name = request_args.get(BLOCKCHAIN_NAME_FIELD_NAME)
        stream_name = request_args.get(STREAM_NAME_FIELD_NAME)
        publishers = request_args.getlist(PUBLISHERS_PARAMETER_NAME)
        verbose = DataController.DEFAULT_VERBOSE_VALUE

        if blockchain_name is None:
            return (
                jsonify(
                    {
                        "error": "The "
                        + BLOCKCHAIN_NAME_FIELD_NAME
                        + " parameter was not found in the request!"
                    }
                ),
                status.HTTP_400_BAD_REQUEST,
            )

        if stream_name is None:
            return (
                jsonify(
                    {
                        "error": "The "
                        + STREAM_NAME_FIELD_NAME
                        + " parameter was not found in the request!"
                    }
                ),
                status.HTTP_400_BAD_REQUEST,
            )

        if not publishers:
            return (
                jsonify(
                    {
                        "error": "The "
                        + PUBLISHERS_PARAMETER_NAME
                        + " parameter was not found in the request!"
                    }
                ),
                status.HTTP_400_BAD_REQUEST,
            )

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

        if not isinstance(publishers, list):
            return (
                jsonify({"error": "You must pass a list of publishers"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not request_args.get(VERBOSE_FIELD_NAME) is None:
            verbose = convert_to_boolean(
                VERBOSE_FIELD_NAME, request_args.get(VERBOSE_FIELD_NAME)
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
The following data is expected to be passed in as query parameters:
    "blockchainName": blockchain name
    "streamName": stream name
    OPTIONAL: "verbose": Set verbose to true for additional information about each item’s transaction
    OPTIONAL: "count": retrieve part of the list only ex. only 5 items
    OPTIONAL: "start": deals with the ordering of the data retrieved, with negative start values (like the default) indicating the most recent items
    OPTIONAL: "localOrdering": Set local-ordering to true to order items by when first seen by this node, rather than their order in the chain
"""


@mod.route("/get_stream_items", methods=["GET"])
def get_stream_items():
    try:
        request_args = request.args

        if not request_args:
            return (
                jsonify({"error": "No parameters were passed!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        blockchain_name = request_args.get(BLOCKCHAIN_NAME_FIELD_NAME)
        stream_name = request_args.get(STREAM_NAME_FIELD_NAME)
        verbose = DataController.DEFAULT_VERBOSE_VALUE
        count = DataController.DEFAULT_ITEM_COUNT_VALUE
        start = DataController.DEFAULT_ITEM_START_VALUE
        local_ordering = DataController.DEFAULT_LOCAL_ORDERING_VALUE

        if blockchain_name is None:
            return (
                jsonify(
                    {
                        "error": "The "
                        + BLOCKCHAIN_NAME_FIELD_NAME
                        + " parameter was not found in the request!"
                    }
                ),
                status.HTTP_400_BAD_REQUEST,
            )

        if stream_name is None:
            return (
                jsonify(
                    {
                        "error": "The "
                        + STREAM_NAME_FIELD_NAME
                        + " parameter was not found in the request!"
                    }
                ),
                status.HTTP_400_BAD_REQUEST,
            )

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

        if not request_args.get(VERBOSE_FIELD_NAME) is None:
            verbose = convert_to_boolean(
                VERBOSE_FIELD_NAME, request_args.get(VERBOSE_FIELD_NAME)
            )

        if not request_args.get(COUNT_FIELD_NAME) is None:
            count = convert_to_int(COUNT_FIELD_NAME, request_args.get(COUNT_FIELD_NAME))

        if not request_args.get(START_FIELD_NAME) is None:
            start = convert_to_int(START_FIELD_NAME, request_args.get(START_FIELD_NAME))

        if not request_args.get(LOCAL_ORDERING_FIELD_NAME) is None:
            local_ordering = convert_to_int(
                LOCAL_ORDERING_FIELD_NAME, request_args.get(LOCAL_ORDERING_FIELD_NAME)
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
The following data is expected to be passed in as query parameters:
    "blockchainName": blockchain name
    "streamName": stream name
    OPTIONAL: "publishers": list of publishers wallet address. This will cause the function to only return information related to the publishers in the list
    OPTIONAL: "verbose": Set verbose to true for additional information about each item’s transaction
    OPTIONAL: "count": retrieve part of the list only ex. only 5 items
    OPTIONAL: "start": deals with the ordering of the data retrieved, with negative start values (like the default) indicating the most recent items
    OPTIONAL: "localOrdering": Set local-ordering to true to order items by when first seen by this node, rather than their order in the chain
"""


@mod.route("/get_stream_publishers", methods=["GET"])
def get_stream_publishers():
    try:
        request_args = request.args

        if not request_args:
            return (
                jsonify({"error": "No parameters were passed!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        blockchain_name = request_args.get(BLOCKCHAIN_NAME_FIELD_NAME)
        stream_name = request_args.get(STREAM_NAME_FIELD_NAME)
        publishers = DataController.DEFAULT_PUBLISHERS_LIST_CONTENT
        verbose = DataController.DEFAULT_VERBOSE_VALUE
        count = DataController.DEFAULT_ITEM_COUNT_VALUE
        start = DataController.DEFAULT_ITEM_START_VALUE
        local_ordering = DataController.DEFAULT_LOCAL_ORDERING_VALUE

        if blockchain_name is None:
            return (
                jsonify(
                    {
                        "error": "The "
                        + BLOCKCHAIN_NAME_FIELD_NAME
                        + " parameter was not found in the request!"
                    }
                ),
                status.HTTP_400_BAD_REQUEST,
            )

        if stream_name is None:
            return (
                jsonify(
                    {
                        "error": "The "
                        + STREAM_NAME_FIELD_NAME
                        + " parameter was not found in the request!"
                    }
                ),
                status.HTTP_400_BAD_REQUEST,
            )

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

        if request_args.get(PUBLISHERS_FIELD_NAME):
            publishers = request_args.getlist(PUBLISHERS_PARAMETER_NAME)
            if not publishers:
                return (
                    jsonify({"error": "The list of publishers can't be empty!"}),
                    status.HTTP_400_BAD_REQUEST,
                )
            if not isinstance(publishers, list):
                return (
                    jsonify({"error": "You must pass a list of publishers"}),
                    status.HTTP_400_BAD_REQUEST,
                )

        if not request_args.get(VERBOSE_FIELD_NAME) is None:
            verbose = convert_to_boolean(
                VERBOSE_FIELD_NAME, request_args.get(VERBOSE_FIELD_NAME)
            )

        if not request_args.get(COUNT_FIELD_NAME) is None:
            count = convert_to_int(COUNT_FIELD_NAME, request_args.get(COUNT_FIELD_NAME))

        if not request_args.get(START_FIELD_NAME) is None:
            start = convert_to_int(START_FIELD_NAME, request_args.get(START_FIELD_NAME))

        if not request_args.get(LOCAL_ORDERING_FIELD_NAME) is None:
            local_ordering = convert_to_int(
                LOCAL_ORDERING_FIELD_NAME, request_args.get(LOCAL_ORDERING_FIELD_NAME)
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

