from plumbum import local, FG, BG, TF, RETCODE
import json


class DataStreamController:
    def __init__(self):
        self._multichain = local['multichain-cli']
        self._create = self._multichain['create']
        self._create_stream = self._create['stream']
        self._get_streams = self._multichain['liststreams']
        self._publish_item = self._multichain['publish']
        self._subscribe_to_stream = self._multichain['subscribe']
        self._unsubscribe_from_stream = self._multichain['unsubscribe']
        self._get_stream_item = self._multichain['getstreamitem']
        self._get_stream_key_items = self._multichain['liststreamkeyitems']
        self._get_stream_keys = self._multichain['liststreamkeys']
        self._get_stream_items = self._multichain['liststreamitems']
        self._get_stream_publisher_items = self._multichain['liststreampublisheritems']
        self._get_stream_publishers = self._multichain['liststreampublishers']

    def create_stream(self, name: str, isOpen: bool):
        """
        Creates a new stream on the blockchain called name. 
        Pass the value "stream" in the type parameter. If open is true 
        then anyone with global send permissions can publish to the stream, 
        otherwise publishers must be explicitly granted per-stream write permissions. 
        Returns the txid of the transaction creating the stream.
        """
        try:

            txid = self._create_stream(name, str(isOpen))
            # need to validate output to ensure that everything is ok
            return txid
        except Exception as err:
            print(err)
    
    def get_streams(self, verbose: bool, names: list = None):
        """
        Returns information about streams created on the blockchain. Pass a stream name, ref or
        creation txid in streams to retrieve information about one stream only, an array thereof 
        for multiple streams, or * for all streams. Use count and start to retrieve part of the 
        list only, with negative start values (like the default) indicating the most recently 
        created streams. Extra fields are shown for streams to which this node has subscribed.
        """
        try:
            if names is not None:
                streams = self._get_streams(str(names), str(verbose))
            else:
                streams = self._get_streams('*', str(verbose))
            # need to validate output
            return streams
        except Exception as err:
            print(err)
        
    
    def publish_item(self, stream_name: str, keys: list, data: str):
        """
        Publishes an item in stream, passed as a stream name, an array of keys 
        and data in JSON format.
        """
        try:
            json_data = json.loads(data)
            formatted_data = json.dumps({"json": json_data})
            txid = self._publish_item(stream_name, str(keys), formatted_data)
            return txid
        except ValueError as err:
            print(err)
        except Exception as err:
            print(err)
    
    def subscribe(self, streams: list, rescan: bool = False):
        """
        Instructs the node to start tracking one or more stream(s). 
        These are specified using an array of one or more items. 
        If rescan is true, the node will reindex all items from when the streams 
        were created, as well as those in other subscribed entities. 
        Returns True if successful.
        """
        try:
            output = self._subscribe_to_stream(str(streams), str(rescan))
            if output == 'null':
                return True
            else:
                return False
        except Exception as err:
            print(err)
    
    def unsubscribe(self, streams: list):
        """
        Instructs the node to stop tracking one or more stream(s). 
        Streams are specified using an array of one ore more items.
        """
        try:
            output = self._unsubscribe_from_stream(str(streams))
            if output == 'null':
                return True
            else:
                return False
        except Exception as err:
            print(err)
