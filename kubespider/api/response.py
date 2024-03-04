from flask import jsonify


def success(data=None, code=200, msg="Ok"):
    return jsonify(data=data, code=code, msg=msg)


def param_error(data=None, code=300, msg="Param Error"):
    return jsonify(data=data, code=code, msg=msg)


def authenticate_require(data=None, code=400, msg="Auth Required"):
    return jsonify(data=data, code=code, msg=msg)


def method_not_allowed(data=None, code=405, msg="Method Not Allowed"):
    return jsonify(data=data, code=code, msg=msg)


def server_error(data=None, code=500, msg="Server Error"):
    return jsonify(data=data, code=code, msg=msg)
