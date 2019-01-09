from flask import Flask

app = Flask(__name__)

from app.api.configuration_route import mod
from app.api.system_status_route import mod
from app.api.data_route import mod
from app.api.data_stream_route import mod
from app.api.node_route import mod
from app.api.permission_route import mod


app.register_blueprint(api.configuration_route.mod, url_prefix="/api")
app.register_blueprint(api.system_status_route.mod, url_prefix="/api")
app.register_blueprint(api.data_route.mod, url_prefix="/api")
app.register_blueprint(api.data_stream_route.mod, url_prefix="/api")
app.register_blueprint(api.node_route.mod, url_prefix="/api")
app.register_blueprint(api.permission_route.mod, url_prefix="/api")


