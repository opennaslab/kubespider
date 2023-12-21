from core.api.response import success
from core.api.v2.system import system_blu


@system_blu.route('/healthz', methods=['GET'])
def health_check_handler():
    return success()


@system_blu.route('/ratelimit', methods=['POST'])
def global_download_ratelimit():
    # todo
    return success()


@system_blu.route('/stop', methods=['POST'])
def stop_all_download_task():
    # todo
    return success()
