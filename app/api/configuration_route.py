from flask import Flask, request, jsonify, Blueprint
from flask_api import status
from app.models.configuration.configuration_controller import ConfigurationController


mod = Blueprint('configuration', __name__)

cc = ConfigurationController()

'''
Creates the blockchain with the provided name
The name is expected in the body of the post request using the tag "name"
'''


@mod.route('/create_chain/', methods=['POST'])
def create_chain():
    cc.create_chain(request.json['name'])
    return jsonify({"Chain Status": "Created"})


'''
Configures the parameters in the param.dat using the blockchain name provided
The name is expected in the body of the post request using the tag "name"
The parameters are expected in the body, nested under the tag "params"
The parameter tags are expected as follows:
    "param blockchain_name":
    "param description":
    "param max_block_size": 
    "param target_block_time":
    "param mining_turnover":
'''


@mod.route('/config_parameters/', methods=['POST'])
def config_params():
    try:
        json_request = request.get_json()

        if not json_request:
            return jsonify({'error': 'The request body is empty!'}), status.HTTP_204_NO_CONTENT
            
        cc.config_params(request.json['name'], request.json['params'])
        return jsonify({"File Status": "Changed"})
    except Exception as ex:
        return jsonify({'error': ex}), status.HTTP_400_BAD_REQUEST

'''
Deploys the created chain
The blockchain name is expected in the body using the "blockchainName" tag
'''


@mod.route('/deploy_chain/', methods=['GET'])
def deploy_chain():
    try:
        json_request = request.get_json()

        if not json_request:
            return jsonify({'error': 'The request body is empty!'}), status.HTTP_204_NO_CONTENT

        blockchain_name = json_request['blockchainName']
        if not blockchain_name or not blockchain_name.strip():
            return jsonify({"error": "The blockchain name can't be empty!"}), status.HTTP_400_BAD_REQUEST

        blockchain_name = blockchain_name.strip()
        if cc.deploy_blockchain(blockchain_name):
            return jsonify({"Status": blockchain_name + " Deployed"}), status.HTTP_200_OK
    except Exception as ex:
        return jsonify({'error': ex}), status.HTTP_400_BAD_REQUEST


'''
Returns the node address of the provided blockchain name
The blockchain name is expected in the body using the "blockchainName" tag
'''


@mod.route('/get_node_address/', methods=['GET'])
def get_node_address():
    try:
        json_request = request.get_json()

        if not json_request:
            return jsonify({'error': 'The request body is empty!'}), status.HTTP_204_NO_CONTENT

        blockchain_name = json_request['blockchainName']
        if not blockchain_name or not blockchain_name.strip():
            return jsonify({"error": "The blockchain name can't be empty!"}), status.HTTP_400_BAD_REQUEST

        blockchain_name = blockchain_name.strip()

        return jsonify({"nodeAddress": cc.get_node_address(blockchain_name)}), status.HTTP_200_OK
    except Exception as ex:
        return jsonify({'error': ex}), status.HTTP_400_BAD_REQUEST
