from flask import Flask, request, jsonify, Blueprint
from flask_api import status
from app.models.data.data_stream_controller import DataStreamController
from app.models.exception.multichain_error import MultiChainError
import json


VERBOSE_FIELD_NAME = "verbose"
COUNT_FIELD_NAME = "count"
START_FIELD_NAME = "start"
BLOCKCHAIN_NAME_FIELD_NAME = "blockchainName"
STREAM_NAME_FIELD_NAME = "streamName"
IS_OPEN_FIELD_NAME = "isOpen"
STREAMS_FIELD_NAME = "streams"
STREAMS_PARAMETER_NAME = STREAMS_FIELD_NAME + "[]"
RESCAN_FIELD_NAME = "rescan"

mod = Blueprint("data_stream", __name__)


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
Creates a new stream on the blockchain.
The following data is expected in the body of the request:
    "blockchainName": blockchain name
    "streamName": stream name
    "isOpen":  If open is true then anyone with global send permissions can publish to the stream, otherwise publishers must be explicitly 
    granted per-stream write permissions
"""


@mod.route("/create_stream", methods=["POST"])
def create_stream():
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

        if not STREAM_NAME_FIELD_NAME in json_request:
            raise ValueError(
                "The " + STREAM_NAME_FIELD_NAME + " field was not found in the request!"
            )

        if not IS_OPEN_FIELD_NAME in json_request:
            raise ValueError(
                "The " + IS_OPEN_FIELD_NAME + " field was not found in the request!"
            )

        blockchain_name = json_request[BLOCKCHAIN_NAME_FIELD_NAME]
        stream_name = json_request[STREAM_NAME_FIELD_NAME]
        is_open = convert_to_boolean(
            IS_OPEN_FIELD_NAME, json_request[IS_OPEN_FIELD_NAME]
        )

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The blockchain name can't be empty!")

        if not stream_name or not stream_name.strip():
            raise ValueError("The stream name can't be empty!")

        blockchain_name = blockchain_name.strip()
        stream_name = stream_name.strip()
        DataStreamController.create_stream(blockchain_name, stream_name, is_open)
        return jsonify({"status": stream_name + " created!"}), status.HTTP_200_OK
    except MultiChainError as ex:
        return jsonify(ex.get_info()), status.HTTP_400_BAD_REQUEST
    except (ValueError, Exception) as ex:
        return (jsonify({"error": {"message": str(ex)}}), status.HTTP_400_BAD_REQUEST)


"""
Returns information about streams created on the blockchain
The following data is expected to be passed in as query parameters:
    "blockchainName": blockchain name
    OPTIONAL: "streams": list of stream names. This will cause the function to retrieve only the information about the streams in the list
    OPTIONAL: "verbose": Set verbose to true for additional information about each item’s transaction
    OPTIONAL: "count": retrieve part of the list only ex. only 5 items
    OPTIONAL: "start": deals with the ordering of the data retrieved, with negative start values (like the default) indicating the most recent items
"""


@mod.route("/get_streams", methods=["GET"])
def get_streams():
    try:
        request_args = request.args

        if not request_args:
            raise ValueError("No parameters were passed!")

        blockchain_name = request_args.get(BLOCKCHAIN_NAME_FIELD_NAME)
        streams = DataStreamController.DEFAULT_STREAMS_LIST_CONTENT
        verbose = DataStreamController.DEFAULT_VERBOSE_VALUE
        count = DataStreamController.DEFAULT_STREAM_COUNT_VALUE
        start = DataStreamController.DEFAULT_STREAM_START_VALUE

        if blockchain_name is None:
            raise ValueError(
                "The "
                + BLOCKCHAIN_NAME_FIELD_NAME
                + " parameter was not found in the request!"
            )

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The blockchain name can't be empty!")

        if request_args.getlist(STREAMS_PARAMETER_NAME):
            streams = request_args.getlist(STREAMS_PARAMETER_NAME)

            if not streams:
                raise ValueError("The list of streams can't be empty!")

            if not isinstance(streams, list):
                raise ValueError("You must pass a list of streams")

        if not request_args.get(VERBOSE_FIELD_NAME) is None:
            verbose = convert_to_boolean(
                VERBOSE_FIELD_NAME, request_args.get(VERBOSE_FIELD_NAME)
            )

        if not request_args.get(COUNT_FIELD_NAME) is None:
            count = convert_to_int(COUNT_FIELD_NAME, request_args.get(COUNT_FIELD_NAME))

        if not request_args.get(START_FIELD_NAME) is None:
            start = convert_to_int(START_FIELD_NAME, request_args.get(START_FIELD_NAME))

        blockchain_name = blockchain_name.strip()
        json_data = DataStreamController.get_streams(
            blockchain_name, streams, verbose, count, start
        )
        return jsonify(json_data), status.HTTP_200_OK
    except MultiChainError as ex:
        return jsonify(ex.get_info()), status.HTTP_400_BAD_REQUEST
    except (ValueError, Exception) as ex:
        return (jsonify({"error": {"message": str(ex)}}), status.HTTP_400_BAD_REQUEST)


"""
Instructs the node to start tracking one or more stream(s).
The following data is expected in the body of the request:
    "blockchainName": blockchain name
    "streams": list of streams to subscribe to
    OPTIONAL: "rescan": Set rescan to true to cause the node to reindex all items from when the streams were created, 
    as well as those in other subscribed entities
"""


@mod.route("/subscribe", methods=["POST"])
def subscribe():
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

        if not STREAMS_FIELD_NAME in json_request:
            raise ValueError(
                "The " + STREAMS_FIELD_NAME + " field was not found in the request!"
            )

        blockchain_name = json_request[BLOCKCHAIN_NAME_FIELD_NAME]
        streams = json_request[STREAMS_FIELD_NAME]
        rescan = DataStreamController.DEFAULT_RESCAN_VALUE

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The blockchain name can't be empty!")

        if not streams:
            raise ValueError("The list of streams can't be empty!")

        if not isinstance(streams, list):
            raise ValueError("You must pass a list of streams")

        if RESCAN_FIELD_NAME in json_request:
            rescan = convert_to_boolean(
                RESCAN_FIELD_NAME, json_request[RESCAN_FIELD_NAME]
            )

        blockchain_name = blockchain_name.strip()
        result = DataStreamController.subscribe(blockchain_name, streams, rescan)
        if result:
            return jsonify({"status": "Subscribed successfully!"}), status.HTTP_200_OK
        return (
            jsonify({"status": "Failed to subscribe to stream(s)"}),
            status.HTTP_400_BAD_REQUEST,
        )
    except MultiChainError as ex:
        return jsonify(ex.get_info()), status.HTTP_400_BAD_REQUEST
    except (ValueError, Exception) as ex:
        return (jsonify({"error": {"message": str(ex)}}), status.HTTP_400_BAD_REQUEST)


"""
Instructs the node to stop tracking one or more stream(s)
The following data is expected in the body of the request:
    "blockchainName": blockchain name
    "streams": list of streams to unsubscribe from
"""


@mod.route("/unsubscribe", methods=["POST"])
def unsubscribe():
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

        if not STREAMS_FIELD_NAME in json_request:
            raise ValueError(
                "The " + STREAMS_FIELD_NAME + " field was not found in the request!"
            )

        blockchain_name = json_request[BLOCKCHAIN_NAME_FIELD_NAME]
        streams = json_request[STREAMS_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The blockchain name can't be empty!")

        if not streams:
            raise ValueError("The list of streams can't be empty!")

        if not isinstance(streams, list):
            raise ValueError("You must pass a list of streams")

        blockchain_name = blockchain_name.strip()
        result = DataStreamController.unsubscribe(blockchain_name, streams)
        if result:
            return jsonify({"status": "Unsubscribed successfully!"}), status.HTTP_200_OK
        return (
            jsonify({"status": "Failed to unsubscribe from stream(s)"}),
            status.HTTP_400_BAD_REQUEST,
        )
    except MultiChainError as ex:
        return jsonify(ex.get_info()), status.HTTP_400_BAD_REQUEST
    except (ValueError, Exception) as ex:
        return (jsonify({"error": {"message": str(ex)}}), status.HTTP_400_BAD_REQUEST)

