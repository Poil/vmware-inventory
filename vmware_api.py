from flask import Flask, jsonify
from app.action import Action
from app.config import get_config
import json

app = Flask(__name__)

@app.route('/api/v1/vcenter/<string:vcenter_name>', methods=['GET'])
def vcenter(vcenter_name):
    """ vcenter """
    try:
        a = Action(
            v_server=get_config(vcenter_name, 'ip'),
            v_user=get_config(vcenter_name, 'user'),
            v_passwd=get_config(vcenter_name, 'password')
        )
        a.v_check_login()
        return jsonify({'status': 'success'})
    except:
        return jsonify({'status': "error connecting to VCenter {name}".format(name=vcenter_name)})


@app.route('/api/v1/vcenter/<string:vcenter_name>/datacenter', methods=['GET'])
def datacenter(vcenter_name):
    """ datacenter """
    try:
        a = Action(
            v_server=get_config(vcenter_name, 'ip'),
            v_user=get_config(vcenter_name, 'user'),
            v_passwd=get_config(vcenter_name, 'password')
        )
        return jsonify(res=a.v_get_datacenter())
    except:
        return jsonify({'status': 'error extracting datacenter for VCenter {name}'.format(name=vcenter_name)})


@app.route('/api/v1/vcenter/<string:vcenter_name>/datacenter/<string:datacenter_name>/cluster', methods=['GET'])
def cluster(vcenter_name, datacenter_name):
    """ datastore """
    try:
        a = Action(
            v_server=get_config(vcenter_name, 'ip'),
            v_user=get_config(vcenter_name, 'user'),
            v_passwd=get_config(vcenter_name, 'password')
        )
        return jsonify(a.v_get_cluster(datacenter_name))
    except:
        return jsonify({'status': "error extracting datastore for VCenter {vcenter_name} and Datacenter \
            {datacenter_name}".format(vcenter_name=vcenter_name, datacenter_name=datacenter_name)})

@app.route('/api/v1/vcenter/<string:vcenter_name>/datacenter/<string:datacenter_name>/datastore', methods=['GET'])
def datastore(vcenter_name, datacenter_name):
    """ datastore """
    try:
        a = Action(
            v_server=get_config(vcenter_name, 'ip'),
            v_user=get_config(vcenter_name, 'user'),
            v_passwd=get_config(vcenter_name, 'password')
        )
        return jsonify(a.v_get_datastore(datacenter_name))
    except:
        return jsonify({'status': "error extracting datastore for VCenter {vcenter_name} and Datacenter \
            {datacenter_name}".format(vcenter_name=vcenter_name, datacenter_name=datacenter_name)})


@app.route('/api/v1/vcenter/<string:vcenter_name>/datacenter/<string:datacenter_name>/cluster/<string:cluster_name>/portgroup', methods=['GET'])
def portgroup(vcenter_name, datacenter_name, cluster_name):
    """ datastore """
    try:
        a = Action(
            v_server=get_config(vcenter_name, 'ip'),
            v_user=get_config(vcenter_name, 'user'),
            v_passwd=get_config(vcenter_name, 'password')
        )
        return jsonify(a.v_get_vhost_portgroup(cluster_name))
    except:
        return jsonify({'status': "error extracting datastore for VCenter {vcenter_name} and Datacenter \
            {datacenter_name}".format(vcenter_name=vcenter_name, datacenter_name=datacenter_name)})



if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
