from importlib import import_module
from fastapi import FastAPI


import_module('dst_run.common.log')
app = FastAPI(title='DST RUN', version='0.1.0')
import_module('dst_run.routes.routes')
