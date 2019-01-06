from subprocess import run, CalledProcessError
import json
from app.models.exception.multichain_error import MultiChainError


class DataController:
    MAX_DATA_COUNT = 10
    MULTICHAIN_ARG = "multichain-cli"
    PUBLISH_ITEM_ARG = "publish"
    GET_STREAM_KEY_ITEMS_ARG = "liststreamkeyitems"
    GET_STREAM_KEYS_ITEMS_ARG = "liststreamqueryitems"
    GET_STREAM_KEYS_ARG = "liststreamkeys"
    GET_STERAM_ITEMS_ARG = "liststreamitems"
    GET_STREAM_PUBLISHER_ITEMS_ARG = "liststreampublisheritems"
    GET_STREAM_PUBLISHERS_ARG = "liststreampublishers"
    DEFAULT_VERBOSE_VALUE = False
    DEFAULT_ITEM_COUNT_VALUE = MAX_DATA_COUNT
    DEFAULT_ITEM_START_VALUE = -MAX_DATA_COUNT
    DEFAULT_LOCAL_ORDERING_VALUE = False
    DEFAULT_PUBLISHERS_LIST_CONTENT = None

    @staticmethod
    def publish_item(blockchain_name: str, stream: str, keys: list, json_data: str):
        """
        Publishes an item in stream, passed as a stream name, an array of keys 
        and data in JSON format.
        """
        try:
            blockchain_name = blockchain_name.strip()
            original_number_of_keys = len(keys)
            stream = stream.strip()
            keys = [key.strip() for key in keys if key.strip()]
            new_number_of_keys = len(keys)

            # If any of the provided keys is invalid then an exception is thrown. This is done to prevent MultiChain from
            # overwritting records that belong to existing key(s) that match the valid keys.
            # Example: stream contains KEY1. Provided keys: ['KEY1', '        ']. The second key is invalid, so after cleaning
            # Provided keys: ['KEY1']. This key already exists so the data will be overwritten.
            #
            if new_number_of_keys != original_number_of_keys:
                raise ValueError(
                    "Only "
                    + str(new_number_of_keys)
                    + "/"
                    + str(original_number_of_keys)
                    + " keys are valid. Please check the keys provided"
                )

            if not stream:
                raise ValueError("Stream name can't be empty")

            if not blockchain_name:
                raise ValueError("Blockchain name can't be empty")

            if not keys:
                raise ValueError("key(s) can't be empty")

            # This is used to ensure that the json_data provided is a valid JSON object
            #
            data = json.loads(json_data)
            formatted_data = json.dumps({"json": json_data})
            args = [
                DataController.MULTICHAIN_ARG,
                blockchain_name,
                DataController.PUBLISH_ITEM_ARG,
                stream,
                json.dumps(keys),
                formatted_data,
            ]
            output = run(args, check=True, capture_output=True)

            return output.stdout.strip()
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except ValueError as err:
            raise err
        except Exception as err:
            raise err

    @staticmethod
    def get_items_by_key(
        blockchain_name: str,
        stream: str,
        key: str,
        verbose: bool = DEFAULT_VERBOSE_VALUE,
        count: int = DEFAULT_ITEM_COUNT_VALUE,
        start: int = DEFAULT_ITEM_START_VALUE,
        local_ordering: bool = DEFAULT_LOCAL_ORDERING_VALUE,
    ):
        """
        Retrieves items that belong to the specified key from stream, passed as a stream name to 
        which the node must be subscribed. Set verbose to true for additional 
        information about the item’s transaction. If an item’s data is larger 
        than the maxshowndata runtime parameter, it will be returned as an 
        object whose fields can be used with gettxoutdata.
        """
        try:
            blockchain_name = blockchain_name.strip()
            stream = stream.strip()
            key = key.strip()

            if not stream:
                raise ValueError("Stream name can't be empty")

            if not key:
                raise ValueError("key can't be empty")

            if not blockchain_name:
                raise ValueError("Blockchain name can't be empty")

            args = [
                DataController.MULTICHAIN_ARG,
                blockchain_name,
                DataController.GET_STREAM_KEY_ITEMS_ARG,
                stream,
                key,
                json.dumps(verbose),
                json.dumps(count),
                json.dumps(start),
                json.dumps(local_ordering),
            ]
            items = run(args, check=True, capture_output=True)
            return json.loads(items.stdout)
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            raise err

    @staticmethod
    def get_items_by_keys(
        blockchain_name: str, stream: str, keys: list, verbose: bool = DEFAULT_VERBOSE_VALUE
    ):
        """
        Retrieves items in stream which match all of the specified keys in query. 
        The query is an object with a keys field. The keys field should 
        specify an array of keys. Note that, unlike other stream retrieval APIs, 
        liststreamqueryitems cannot rely completely on prior indexing, 
        so the maxqueryscanitems runtime parameter limits how many 
        items will be scanned after using the best index. If more than 
        this is needed, an error will be returned.
        """
        try:
            blockchain_name = blockchain_name.strip()
            original_number_of_keys = len(keys)
            stream = stream.strip()
            keys = [key.strip() for key in keys if key.strip()]
            new_number_of_keys = len(keys)

            if not stream:
                raise ValueError("Stream name can't be empty")

            # If any of the provided keys is invalid then an exception is thrown. This is done to prevent MultiChain from
            # retrieving records that belong to existing key(s) that match the valid keys.
            # Example: stream contains KEY1. Provided keys: ['KEY1', '        ']. The second key is invalid, so after cleaning
            # Provided keys: ['KEY1']. This key already exists so a different record will be retrieved than what is expected.
            #
            if new_number_of_keys != original_number_of_keys:
                raise ValueError(
                    "Only "
                    + str(new_number_of_keys)
                    + "/"
                    + str(original_number_of_keys)
                    + " keys are valid. Please check the keys provided"
                )

            if not keys:
                raise ValueError("keys can't be empty")

            if not blockchain_name:
                raise ValueError("Blockchain name can't be empty")

            args = [
                DataController.MULTICHAIN_ARG,
                blockchain_name,
                DataController.GET_STREAM_KEYS_ITEMS_ARG,
                stream,
                json.dumps({"keys": keys}),
                json.dumps(verbose),
            ]
            items = run(args, check=True, capture_output=True)

            return json.loads(items.stdout)
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            raise err

    @staticmethod
    def get_items_by_publishers(
        blockchain_name: str, stream: str, publishers: list, verbose: bool = DEFAULT_VERBOSE_VALUE
    ):
        """
        Retrieves items in stream which match all of the specified publishers in query. 
        The query is an object with a publishers field. The publishers field should 
        specify an array of publishers. Note that, unlike other stream retrieval APIs, 
        liststreamqueryitems cannot rely completely on prior indexing, 
        so the maxqueryscanitems runtime parameter limits how many 
        items will be scanned after using the best index. If more than 
        this is needed, an error will be returned.
        """
        try:
            blockchain_name = blockchain_name.strip()
            stream = stream.strip()
            publishers = [
                publisher.strip() for publisher in publishers if publisher.strip()
            ]

            if not stream:
                raise ValueError("Stream name can't be empty")

            if not publishers:
                raise ValueError("Publishers can't be empty")

            if not blockchain_name:
                raise ValueError("Blockchain name can't be empty")

            args = [
                DataController.MULTICHAIN_ARG,
                blockchain_name,
                DataController.GET_STREAM_KEYS_ITEMS_ARG,
                stream,
                json.dumps({"publishers": publishers}),
                json.dumps(verbose),
            ]
            items = run(args, check=True, capture_output=True)

            return json.loads(items.stdout)
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            raise err

    @staticmethod
    def get_items_by_publisher(
        blockchain_name: str,
        stream: str,
        publisher: str,
        verbose: bool = DEFAULT_VERBOSE_VALUE,
        count: int = DEFAULT_ITEM_COUNT_VALUE,
        start: int = DEFAULT_ITEM_START_VALUE,
        local_ordering: bool = DEFAULT_LOCAL_ORDERING_VALUE,
    ):
        """
        Retrieves items that belong to the specified publisher from stream, passed as a stream name to 
        which the node must be subscribed. Set verbose to true for additional 
        information about the item’s transaction. If an item’s data is larger 
        than the maxshowndata runtime parameter, it will be returned as an 
        object whose fields can be used with gettxoutdata.
        """
        try:
            blockchain_name = blockchain_name.strip()
            stream = stream.strip()
            publisher = publisher.strip()

            if not stream:
                raise ValueError("Stream name can't be empty")

            if not publisher:
                raise ValueError("Publisher can't be empty")

            if not blockchain_name:
                raise ValueError("Blockchain name can't be empty")

            args = [
                DataController.MULTICHAIN_ARG,
                blockchain_name,
                DataController.GET_STREAM_PUBLISHER_ITEMS_ARG,
                stream,
                publisher,
                json.dumps(verbose),
                json.dumps(count),
                json.dumps(start),
                json.dumps(local_ordering),
            ]
            items = run(args, check=True, capture_output=True)

            return json.loads(items.stdout)
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            raise err

    @staticmethod
    def get_stream_items(
        blockchain_name: str,
        stream: str,
        verbose: bool = DEFAULT_VERBOSE_VALUE,
        count: int = DEFAULT_ITEM_COUNT_VALUE,
        start: int = DEFAULT_ITEM_START_VALUE,
        local_ordering: bool = DEFAULT_VERBOSE_VALUE,
    ):
        """
        Retrieves items in stream, passed as a stream name. 
        Set verbose to true for additional information about each item’s transaction. 
        Use count and start to retrieve part of the list only, with negative start 
        values (like the default) indicating the most recent items. 
        Set local-ordering to true to order items by when first seen by this node, 
        rather than their order in the chain. If an item’s data is larger than 
        the maxshowndata runtime parameter, it will be returned as an object 
        whose fields can be used with gettxoutdata.
        """
        try:
            blockchain_name = blockchain_name.strip()
            stream = stream.strip()

            if not stream:
                raise ValueError("Stream name can't be empty")

            if not blockchain_name:
                raise ValueError("Blockchain name can't be empty")

            args = [
                DataController.MULTICHAIN_ARG,
                blockchain_name,
                DataController.GET_STERAM_ITEMS_ARG,
                stream,
                json.dumps(verbose),
                json.dumps(count),
                json.dumps(start),
                json.dumps(local_ordering),
            ]
            items = run(args, check=True, capture_output=True)

            return json.loads(items.stdout)
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            raise err

    @staticmethod
    def get_stream_publishers(
        blockchain_name: str,
        stream: str,
        publishers: list = DEFAULT_PUBLISHERS_LIST_CONTENT,
        verbose: bool = DEFAULT_VERBOSE_VALUE,
        count: int = DEFAULT_ITEM_COUNT_VALUE,
        start: int = DEFAULT_ITEM_START_VALUE,
        local_ordering: bool = DEFAULT_LOCAL_ORDERING_VALUE,
    ):
        """
        Provides information about publishers who have written to stream, 
        passed as a stream name. Pass an array for multiple publishers, or 
        use the default value for all publishers. Set verbose to true to include 
        information about  the first and last item by each publisher shown. 
        See liststreamitems for details of the count, start and local-ordering 
        parameters, relevant only if all publishers is requested.
        """
        try:
            blockchain_name = blockchain_name.strip()
            stream = stream.strip()

            if not stream:
                raise ValueError("Stream name can't be empty")

            if not blockchain_name:
                raise ValueError("Blockchain name can't be empty")

            address_selector = "*"
            if publishers is not None:
                publishers = [
                    address.strip() for address in publishers if address.strip()
                ]
                if not publishers:
                    raise ValueError("Addresses can't be empty")
                address_selector = json.dumps(publishers)

            args = [
                DataController.MULTICHAIN_ARG,
                blockchain_name,
                DataController.GET_STREAM_PUBLISHERS_ARG,
                stream,
                address_selector,
                json.dumps(verbose),
                json.dumps(count),
                json.dumps(start),
                json.dumps(local_ordering),
            ]
            publishers = run(args, check=True, capture_output=True)

            return json.loads(publishers.stdout)
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            raise err
