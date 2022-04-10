from importlib import import_module
from fastapi import FastAPI
from dst_run.common.log import log


log.info('start dst-run')
app = FastAPI(title='DST RUN', version='0.1.0')
import_module('dst_run.app.routes.middlewares')
import_module('dst_run.app.routes.routes')
import_module('dst_run.app.routes.action_routes')
import_module('dst_run.app.routes.server_routes')
import_module('dst_run.app.routes.cluster_routes')
import_module('dst_run.app.routes.template_routes')
import_module('dst_run.app.routes.backup_cluster_routes')
import_module('dst_run.app.routes.room_routes')
import_module('dst_run.app.routes.world_routes')
import_module('dst_run.app.routes.mod_routes')
