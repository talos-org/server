#!/usr/bin/env python

from flask import Flask, request, jsonify
from flask_api import status
from configuration_controller import ConfigurationController

'''
Creates an instance of flask, setting name to '__main__' once the script is run
'''
app = Flask(__name__)

cc = ConfigurationController()

'''
Creates the blockchain with the provided name
The name is expected in the body of the post request using the tag "name"
'''
@app.route('/create_chain/', methods=['POST'])
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
@app.route('/config_parameters/', methods=['POST'])
def config_params():
    cc.config_params(request.json['name'],request.json['params'])
    return jsonify({"File Status": "Changed"})


'''
Deploys the created chain
The blockchain name is expected in the header using the "name" tag
'''
@app.route('/deploy_chain/', methods=['GET'])
def deploy_chain():
    if (cc.deploy_blockchain(request.args.get('name'))):
        return jsonify({"Status": "Deployed"}), status.HTTP_200_OK
    return jsonify({"Status": "Failure"}), status.HTTP_400_BAD_REQUEST

'''
Returns the node address of the provided blockchain name
The blockchain name is expected in the header using the "name" tag
'''
@app.route('/get_node_address/', methods=['GET'])
def get_node_address():
    return jsonify({"Node Address" :cc.get_node_address(request.args.get('name'))})



if __name__ == '__main__':
    app.run(debug=True)