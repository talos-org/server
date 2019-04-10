[![Total alerts](https://img.shields.io/lgtm/alerts/g/talos-org/server.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/talos-org/server/alerts/)

# server v0.1.0-alpha

Backend for Talos, a configurable platform for developing and deploying blockchains

> WARNING: Talos is still in the Alpha development phase and is intended for experimenting and learning. Talos is currently not ready for use in production environments.

The Talos server works well with the [Talos client](https://github.com/talos-org/client), however the Talos server can also be used on its own or with a client of your choice.

# Prerequisites
- Python 3.7
- pip3
- Git
- Linux Machine (Mac and Windows support will be added at a later time)

# Installation
`$ git clone https://github.com/talos-org/server.git`

`$ cd server`

`$ python3 -m venv venv`

`$ source venv/bin/activate`

`(venv) $ pip3 install -r requirements.txt`

# Install MultiChain

Make sure you are in the `server` directory then run the following commands:<br>
`$ chmod +x multichain.sh`

`$ sudo ./multichain.sh`

# Start server
Make sure you are in the `server` directory and you are still in the virtual environment then run the following command:<br>
`(venv) $ python3 run.py`

The server should now be running and listening for requests (e.g. from the talos client) on port 5000

# View Swagger API Documentation (Optional)
Visit http://localhost:5000/api/ on your web browser

This web page presents the available REST endpoints provided by the talos server and allows you to try them out
