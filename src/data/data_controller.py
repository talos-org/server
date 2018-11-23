from subprocess import run, CalledProcessError
from shlex import quote
import json


class DataController:
    MAX_DATA_COUNT = 10

    def __init__(self, blockchain_name: str):
        self._multichain_arg = ['multichain-cli', quote(blockchain_name)]
        self._publish_item_arg = self._multichain_arg + ['publish']
        self._get_stream_key_items_arg = self._multichain_arg + \
            ['liststreamkeyitems']
        self._get_stream_keys_items_arg = self._multichain_arg + \
            ['liststreamqueryitems']
        self._get_stream_keys_arg = self._multichain_arg + ['liststreamkeys']
        self._get_stream_items_arg = self._multichain_arg + ['liststreamitems']
        self._get_stream_publisher_items_arg = self._multichain_arg + \
            ['liststreampublisheritems']
        self._get_stream_publishers_arg = self._multichain_arg + \
            ['liststreampublishers']

    def publish_item(self, stream: str, keys: list, data: str):
        """
        Publishes an item in stream, passed as a stream name, an array of keys 
        and data in JSON format.
        """
        try:
            json_data = json.loads(data)
            formatted_data = json.dumps({"json": json_data})
            args = self._publish_item_arg + \
                [quote(stream), json.dumps(keys), formatted_data]
            output = run(args, check=True, capture_output=True)

            return output.stdout.strip()
        except CalledProcessError as err:
            print(err.stderr)
        except ValueError as err:
            print(err)
        except Exception as err:
            print(err)

    def get_items_by_key(self, stream: str, key: str,  verbose: bool = False, count: int = MAX_DATA_COUNT, start: int = -MAX_DATA_COUNT, local_ordering: bool = False):
        """
        Retrieves items that belong to the specified key from stream, passed as a stream name to 
        which the node must be subscribed. Set verbose to true for additional 
        information about the item’s transaction. If an item’s data is larger 
        than the maxshowndata runtime parameter, it will be returned as an 
        object whose fields can be used with gettxoutdata.
        """
        try:
            args = self._get_stream_key_items_arg + [quote(stream), quote(key), json.dumps(
                verbose), json.dumps(count), json.dumps(start), json.dumps(local_ordering)]
            items = run(args, check=True, capture_output=True)

            return json.loads(items.stdout)
        except CalledProcessError as err:
            print(err.stderr)
        except Exception as err:
            print(err)

    def get_items_by_keys(self, stream: str, keys: list,  verbose: bool = False):
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
            args = self._get_stream_keys_items_arg + \
                [quote(stream), json.dumps(
                    {"keys": keys}), json.dumps(verbose)]
            items = run(args, check=True, capture_output=True)

            return json.loads(items.stdout)
        except CalledProcessError as err:
            print(err.stderr)
        except Exception as err:
            print(err)

    def get_items_by_publishers(self, stream: str, publishers: list, verbose: bool = False):
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
            args = self._get_stream_keys_items_arg + \
                [quote(stream), json.dumps({"publishers": publishers}),
                 json.dumps(verbose)]
            items = run(args, check=True, capture_output=True)

            return json.loads(items.stdout)
        except CalledProcessError as err:
            print(err.stderr)
        except Exception as err:
            print(err)

    def get_items_by_publisher(self, stream: str, publisher: str,  verbose: bool = False, count: int = MAX_DATA_COUNT, start: int = -MAX_DATA_COUNT, local_ordering: bool = False):
        """
        Retrieves items that belong to the specified publisher from stream, passed as a stream name to 
        which the node must be subscribed. Set verbose to true for additional 
        information about the item’s transaction. If an item’s data is larger 
        than the maxshowndata runtime parameter, it will be returned as an 
        object whose fields can be used with gettxoutdata.
        """
        try:
            args = self._get_stream_publisher_items_arg + [quote(stream), quote(publisher), json.dumps(
                verbose), json.dumps(count), json.dumps(start), json.dumps(local_ordering)]
            items = run(args, check=True, capture_output=True)

            return json.loads(items.stdout)
        except CalledProcessError as err:
            print(err.stderr)
        except Exception as err:
            print(err)

    def get_stream_items(self, stream: str, verbose: bool = False, count: int = MAX_DATA_COUNT, start: int = -MAX_DATA_COUNT, local_ordering: bool = False):
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
            args = self._get_stream_items_arg + [quote(stream), json.dumps(
                verbose), json.dumps(count), json.dumps(start), json.dumps(local_ordering)]
            items = run(args, check=True, capture_output=True)

            return json.loads(items.stdout)
        except CalledProcessError as err:
            print(err.stderr)
        except Exception as err:
            print(err)

    def get_stream_publishers(self, stream: str, addresses: list = None, verbose: bool = False, count: int = MAX_DATA_COUNT, start: int = -MAX_DATA_COUNT, local_ordering: bool = False):
        """
        Provides information about publishers who have written to stream, 
        passed as a stream name. Pass an array for multiple publishers, or 
        use the default value for all publishers. Set verbose to true to include 
        information about  the first and last item by each publisher shown. 
        See liststreamitems for details of the count, start and local-ordering 
        parameters, relevant only if all publishers is requested.
        """
        try:
            address_selector = '*'
            if addresses is not None:
                address_selector = json.dumps(addresses)

            args = self._get_stream_publishers_arg + [quote(stream), address_selector,  json.dumps(
                verbose), json.dumps(count), json.dumps(start), json.dumps(local_ordering)]
            publishers = run(args, check=True, capture_output=True)

            return json.loads(publishers.stdout)
        except CalledProcessError as err:
            print(err.stderr)
        except Exception as err:
            print(err)
