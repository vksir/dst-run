from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from dst_run.common.log import log
from dst_run.app import middlewares
from dst_run.app.routes import routes
from dst_run.app.routes import action_routes
from dst_run.app.routes import server_routes
from dst_run.app.routes import cluster_routes
from dst_run.app.routes import template_routes
from dst_run.app.routes import backup_cluster_routes
from dst_run.app.routes import room_routes
from dst_run.app.routes import world_routes
from dst_run.app.routes import mod_routes


log.info('start dst-run')
app = FastAPI(title='DST RUN', version='0.1.0')
app.add_middleware(BaseHTTPMiddleware,
                   dispatch=middlewares.add_process_time_header)
app.include_router(routes.router)
app.include_router(action_routes.router)
app.include_router(server_routes.router)
app.include_router(cluster_routes.router)
app.include_router(template_routes.router)
app.include_router(backup_cluster_routes.router)
app.include_router(room_routes.router)
app.include_router(world_routes.router)
app.include_router(mod_routes.router)

