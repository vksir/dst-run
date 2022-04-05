from dst_run.app.app import app


@app.get('/system/status', tags=['system'])
async def system_status():
    pass
