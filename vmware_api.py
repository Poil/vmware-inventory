from flask import Flask, jsonify, request
from flask_caching import Cache
from app.action import Action
from app.config import get_config, get_vcenters
import json

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

def make_cache_key(*args, **kwargs):
    """ make cache key """
    path = request.path
    args = str(hash(frozenset(request.args.items())))
    return (path + args).encode('utf-8')


@app.route('/api/v1/vcenter', methods=['GET'])
def vcenters():
    """ vcenter """
    try:
        return jsonify(get_vcenters())
    except Exception:
        return jsonify({'status': "error reading configuration file"})


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
    except Exception:
        return jsonify({'status': "error connecting to VCenter {name}".format(name=vcenter_name)})


@app.route('/api/v1/vcenter/<string:vcenter_name>/<string:prop_name>', methods=['GET'])
def vcenter_property(vcenter_name, prop_name):
    """ vcenter """
    ret = json.dumps(get_config(vcenter_name, prop_name))
    resp = app.response_class(response=ret, status=200, mimetype="application/json")
    return resp


@app.route('/api/v1/vcenter/<string:vcenter_name>/template', methods=['GET'])
@cache.cached(timeout=7200, key_prefix=make_cache_key)
def template(vcenter_name):
    """ template """
    try:
        a = Action(
            v_server=get_config(vcenter_name, 'ip'),
            v_user=get_config(vcenter_name, 'user'),
            v_passwd=get_config(vcenter_name, 'password')
        )
        ret = json.dumps(a.v_get_vm_template())
        resp = app.response_class(response=ret, status=200, mimetype="application/json")
        return resp
    except Exception:
        return jsonify({'status': 'error extracting template for VCenter {name}'.format(name=vcenter_name)})


@app.route('/api/v1/vcenter/<string:vcenter_name>/datacenter', methods=['GET'])
@cache.cached(timeout=7200, key_prefix=make_cache_key)
def datacenter(vcenter_name):
    """ datacenter """
    try:
        a = Action(
            v_server=get_config(vcenter_name, 'ip'),
            v_user=get_config(vcenter_name, 'user'),
            v_passwd=get_config(vcenter_name, 'password')
        )
        ret = json.dumps(a.v_get_datacenter())
        resp = app.response_class(response=ret, status=200, mimetype="application/json")
        return resp
    except Exception:
        return jsonify({'status': 'error extracting datacenter for VCenter {name}'.format(name=vcenter_name)})


@app.route('/api/v1/vcenter/<string:vcenter_name>/datacenter/<string:datacenter_name>/cluster', methods=['GET'])
@cache.cached(timeout=7200, key_prefix=make_cache_key)
def cluster(vcenter_name, datacenter_name):
    """ cluster """
    try:
        oformat = request.args.get('format', default='full', type=str)
        a = Action(
            v_server=get_config(vcenter_name, 'ip'),
            v_user=get_config(vcenter_name, 'user'),
            v_passwd=get_config(vcenter_name, 'password')
        )
        if oformat == 'full':
            return jsonify(a.v_get_cluster(datacenter_name))
        ret = json.dumps(a.v_get_cluster(datacenter_name)[datacenter_name].keys())
        resp = app.response_class(response=ret, status=200, mimetype="application/json")
        return resp
    except Exception:
        return jsonify({'status': "error extracting datastore for VCenter {vcenter_name} and Datacenter \
            {datacenter_name}".format(vcenter_name=vcenter_name, datacenter_name=datacenter_name)})


@app.route('/api/v1/vcenter/<string:vcenter_name>/datacenter/<string:datacenter_name>/datastore', methods=['GET'])
@cache.cached(timeout=7200, key_prefix=make_cache_key)
def datastore(vcenter_name, datacenter_name):
    """ datastore """
    try:
        oformat = request.args.get('format', default='full', type=str)
        a = Action(
            v_server=get_config(vcenter_name, 'ip'),
            v_user=get_config(vcenter_name, 'user'),
            v_passwd=get_config(vcenter_name, 'password')
        )
        if oformat == 'full':
            return jsonify(a.v_get_datastore(datacenter_name))
        else:
            ret = json.dumps(a.v_get_datastore(datacenter_name)[datacenter_name].keys())
            resp = app.response_class(response=ret, status=200, mimetype="application/json")
            return resp
    except Exception:
        return jsonify({'status': "error extracting datastore for VCenter {vcenter_name} and Datacenter \
            {datacenter_name}".format(vcenter_name=vcenter_name, datacenter_name=datacenter_name)})


@app.route('/api/v1/vcenter/<string:vcenter_name>/datacenter/<string:datacenter_name>/vdswitch', methods=['GET'])
@cache.cached(timeout=7200, key_prefix=make_cache_key)
def vdswitch(vcenter_name, datacenter_name):
    """ vsdswitch """
    try:
        oformat = request.args.get('format', default='full', type=str)
        a = Action(
            v_server=get_config(vcenter_name, 'ip'),
            v_user=get_config(vcenter_name, 'user'),
            v_passwd=get_config(vcenter_name, 'password')
        )
        if oformat == 'full':
            return jsonify(a.v_get_vdswitch())
        ret = json.dumps(a.v_get_vdswitch(datacenter_name)[datacenter_name])
        resp = app.response_class(response=ret, status=200, mimetype="application/json")
        return resp
    except Exception:
        return jsonify({'status': "error extracting datastore for VCenter {vcenter_name} and Datacenter \
            {datacenter_name}".format(vcenter_name=vcenter_name, datacenter_name=datacenter_name)})


@app.route('/api/v1/vcenter/<string:vcenter_name>/datacenter/<string:datacenter_name>/vdswitch/<string:vdswitch_name>/vdportgroup', methods=['GET'])
@cache.cached(timeout=7200, key_prefix=make_cache_key)
def vdportgroup(vcenter_name, vdswitch_name, datacenter_name):
    """ vdportgroup """
    try:
        oformat = request.args.get('format', default='full', type=str)
        a = Action(
            v_server=get_config(vcenter_name, 'ip'),
            v_user=get_config(vcenter_name, 'user'),
            v_passwd=get_config(vcenter_name, 'password')
        )
        ret = json.dumps(a.v_get_vdportgroup(datacenter_name, vdswitch_name))
        resp = app.response_class(response=ret, status=200, mimetype="application/json")
        return resp
    except Exception:
        return jsonify({'status': "error extracting vdportgroup for VCenter {vcenter_name} and Datacenter \
            {datacenter_name}".format(vcenter_name=vcenter_name, datacenter_name=datacenter_name)})


@app.route('/api/v1/vcenter/<string:vcenter_name>/datacenter/<string:datacenter_name>/datastore/<string:datastore_name>/folder', methods=['GET'])
@cache.cached(timeout=7200, key_prefix=make_cache_key)
def folder(vcenter_name, datacenter_name, datastore_name):
    """ folder """
    try:
        oformat = request.args.get('format', default='full', type=str)
        a = Action(
            v_server=get_config(vcenter_name, 'ip'),
            v_user=get_config(vcenter_name, 'user'),
            v_passwd=get_config(vcenter_name, 'password')
        )
        if oformat == 'full':
            return jsonify(a.v_get_folder(datacenter_name, datastore_name))
        ret = json.dumps(a.v_get_folder(datacenter_name, datastore_name)[datacenter_name][datastore_name])
        resp = app.response_class(response=ret, status=200, mimetype="application/json")
        return resp
    except Exception:
        return jsonify({'status': "error extracting datastore for VCenter {vcenter_name} and Datacenter \
            {datacenter_name}".format(vcenter_name=vcenter_name, datacenter_name=datacenter_name)})


@app.route('/api/v1/vcenter/<string:vcenter_name>/datacenter/<string:datacenter_name>/vmfolder', methods=['GET'])
@cache.cached(timeout=7200, key_prefix=make_cache_key)
def vmfolder(vcenter_name, datacenter_name):
    """ folder """
    try:
        oformat = request.args.get('format', default='full', type=str)
        a = Action(
            v_server=get_config(vcenter_name, 'ip'),
            v_user=get_config(vcenter_name, 'user'),
            v_passwd=get_config(vcenter_name, 'password')
        )
        if oformat == 'full':
            return jsonify(a.v_get_vmfolder(datacenter_name))
        ret = json.dumps(a.v_get_vmfolder(datacenter_name))
        resp = app.response_class(response=ret, status=200, mimetype="application/json")
        return resp
    except Exception:
        return jsonify({'status': "error extracting vmfolder for VCenter {vcenter_name} and Datacenter \
            {datacenter_name}".format(vcenter_name=vcenter_name, datacenter_name=datacenter_name)})


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
