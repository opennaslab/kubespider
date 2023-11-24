from flask import request, current_app
from sqlalchemy import or_

from core.api.response import param_error, success
from core.api.v2.resource import resource_blu
from core.models import db
from core.models import Resource as ResourceModel
from utils.values import Resource as DownloadResource


@resource_blu.route("/search", methods=["POST"])
def search_resource():
    keyword = request.json.get("keyword")
    sync = request.json.get("sync",True)
    if not keyword:
        return param_error(msg="keyword missing")
    source_manager = current_app.extensions["source_manager"]
    result = source_manager.search(keyword=keyword, sync=sync)
    return success(result)


@resource_blu.route("/list", methods=["POST"])
def list_resource():
    # todo
    if request.method == 'GET':
        keyword = request.args.get("keyword", "")
        resource = ResourceModel.query.filter(or_(ResourceModel.title.like(f"%{keyword}%"))).all()
        return success([r.to_dict() for r in resource])
    else:
        resource_id = request.json.get("resource_id", "")
        resource = ResourceModel.query.filter(ResourceModel.uuid == resource_id).first()
        if not resource:
            return param_error(msg='Resource not exist')
        db.session.delete(resource)
        db.session.commit()
        return success()


@resource_blu.route("/receive", methods=["POST"])
def receive_resource_from_source_provider():
    # todo
    resources = request.json.get("resources", [])
    resource_objs = [ResourceModel.init_model(**r) for r in resources]
    db.session.add_all(resource_objs)
    db.session.commit()
    return success()


@resource_blu.route("/download", methods=["POST"])
def download_resource():
    # todo
    statemachine_manager = current_app.extensions['statemachine_manager']
    uuid = request.json.get("uuid")
    path = request.json.get('path', '')
    download_provider_id = request.json.get('download_provider_id')
    if uuid:
        resource = ResourceModel.query.filter(ResourceModel.uuid == uuid).first()
        if not resource:
            return param_error(msg='Resource not exist')
        resource = resource.to_dict()
        resource['path'] = path
        resource['download_provider_id'] = download_provider_id
    else:
        source = request.json.get('source')
        uuid = DownloadResource.get_uuid(url=source)
        if not source:
            return param_error(msg="Invalid resource")
        resource = {
            "url": request.json.get('source'),
            "path": request.json.get('path'),
            "uuid": uuid,
            "download_provider_id": download_provider_id,
        }
    err = statemachine_manager.create_state_machine(DownloadResource(**resource))
    if not err:
        return success()
    else:
        return param_error(msg=err)
