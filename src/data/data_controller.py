from plumbum import local, FG, BG, TF, RETCODE, ProcessExecutionError
import json


class DataController:
    MAX_DATA_COUNT = 10

    def __init__(self):
        self._multichain = local['multichain-cli']['talos']
        self._publish_item = self._multichain['publish']
        self._get_stream_item = self._multichain['getstreamitem']
        self._get_stream_key_items = self._multichain['liststreamkeyitems']
        self._get_stream_keys_items = self._multichain['liststreamqueryitems']
        self._get_stream_keys = self._multichain['liststreamkeys']
        self._get_stream_items = self._multichain['liststreamitems']
        self._get_stream_publisher_items = self._multichain['liststreampublisheritems']
        self._get_stream_publishers = self._multichain['liststreampublishers']

    def publish_item(self, stream: str, keys: list, data: str):
        """
        Publishes an item in stream, passed as a stream name, an array of keys 
        and data in JSON format.
        """
        try:
            json_data = json.loads(data)
            formatted_data = json.dumps({"json": json_data})
            output = self._publish_item[
                stream, json.dumps(keys), formatted_data].run(retcode = 0)
                
            return output[1].strip()
        except ProcessExecutionError as err:
            print(err.args[3])
        except ValueError as err:
            print(err)
        except Exception as err:
            print(err)

    def getItemsByKey(self, stream: str, key: str,  verbose: bool = False, count: int = MAX_DATA_COUNT, start: int = -MAX_DATA_COUNT, local_ordering: bool = False):
        """
        Retrieves a specific item with key from stream, passed as a stream name to 
        which the node must be subscribed. Set verbose to true for additional 
        information about the item’s transaction. If an item’s data is larger 
        than the maxshowndata runtime parameter, it will be returned as an 
        object whose fields can be used with gettxoutdata.
        """
        try:
            items = self._get_stream_key_items[stream, key, json.dumps(
                verbose), json.dumps(count), json.dumps(start), json.dumps(local_ordering)].run(retcode = 0)

            return items[1].strip()
        except ProcessExecutionError as err:
            print(err.args[3])
        except Exception as err:
            print(err)

    def getItemsByKeys(self, stream: str, keys: list,  verbose: bool = False):
        """
        This works like liststreamitems, but listing items in stream which match 
        all of the specified keys and/or publishers in query. The query is an 
        object with a key or keys field, and/or a publisher or publishers field. 
        If present, key and publisher should specify a single key or 
        publisher respectively, whereas keys and publishers should 
        specify arrays thereof. Note that, unlike other stream retrieval APIs, 
        liststreamqueryitems cannot rely completely on prior indexing, 
        so the maxqueryscanitems runtime parameter limits how many 
        items will be scanned after using the best index. If more than 
        this is needed, an error will be returned.
        """
        try:
            items = self._get_stream_keys_items[
                stream, json.dumps(keys), json.dumps(verbose)].run(retcode = 0)

            return items[1].strip()
        except ProcessExecutionError as err:
            print(err.args[3])
        except Exception as err:
            print(err)

    def getItemsByPublisher(self, stream: str, publishers: list, verbose: bool = False):
        return True
