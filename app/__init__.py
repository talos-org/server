from flask import Flask, Blueprint
from flask_cors import CORS
from flask_api import status
from flask_restplus import Api

from app.api.configuration_route import config_ns
from app.api.data_route import data_ns
from app.api.node_route import node_ns
from app.api.network_route import network_ns
from app.api.data_stream_route import data_stream_ns
from app.api.permission_route import permission_ns

from app.models.exception.multichain_error import MultiChainError

app = Flask(__name__)
CORS(app)

blueprint = Blueprint("api", __name__, url_prefix="/api")

api = Api(
    blueprint,
    title="Talos",
    version="1.0",
    description="A configurable platform for developing and deploying blockchains",
)

api.add_namespace(config_ns)
api.add_namespace(data_ns)
api.add_namespace(node_ns)
api.add_namespace(network_ns)
api.add_namespace(data_stream_ns)
api.add_namespace(permission_ns)

app.register_blueprint(blueprint)


@api.errorhandler(Exception)
def handle_root_exception(error):
    return {"error": {"message": str(error)}}, status.HTTP_400_BAD_REQUEST


@api.errorhandler(ValueError)
def handle_value_exception(error):
    return {"error": {"message": str(error)}}, status.HTTP_400_BAD_REQUEST


@api.errorhandler(MultiChainError)
def handle_multichain_exception(error):
    return error.get_info(), status.HTTP_400_BAD_REQUEST
