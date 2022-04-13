from fastapi import APIRouter


router = APIRouter(tags=['system'])


@router.get('/system/status')
async def system_status():
    pass
