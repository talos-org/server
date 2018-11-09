from plumbum import local, FG, BG, TF, RETCODE


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

    def create_stream(self, name, isOpen):
        """
        Creates a new stream on the blockchain called name. Pass the value "stream" in the type 
        parameter (the create API can also be used to create upgrades). If open is true then 
        anyone with global send permissions can publish to the stream, otherwise publishers 
        must be explicitly granted per-stream write permissions. Returns the txid of the transaction creating the stream.
        """
        txid = self._create_stream(name, str(isOpen))
        # need to validate output to ensure that everything is ok
        return txid
    
    def get_streams(self, verbose, names = None):
        """
        Returns information about streams created on the blockchain. Pass a stream name, ref or
        creation txid in streams to retrieve information about one stream only, an array thereof 
        for multiple streams, or * for all streams. Use count and start to retrieve part of the 
        list only, with negative start values (like the default) indicating the most recently 
        created streams. Extra fields are shown for streams to which this node has subscribed.
        """
        if names is not None:
            streams = self._get_streams(names, str(verbose))
        else:
            streams = self._get_streams('*', str(verbose))
        # need to validate output
        return streams
    
    def publish_item(self, stream_name, keys, data, data_type = 'json'):
        """
        Publishes an item in stream, passed as a stream name, ref or creation txid, 
        with key provided in text form or an array of keys and data in text or JSON (set in the data type field).
        """
        txid = self._publish_item(stream_name, str(keys), '{{"{0}":{1}}}'.format(data_type, data))
        return txid
