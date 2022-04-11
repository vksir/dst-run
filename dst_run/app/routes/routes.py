from fastapi import APIRouter
from fastapi import Depends
from dst_run.app.dependencies import verify_token
from dst_run.app.models.response_models import Response


router = APIRouter(tags=['system'],
                   dependencies=[Depends(verify_token)])


@router.get('/system/status')
async def system_status():
    pass
