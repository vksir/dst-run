import uvicorn
import platform


if __name__ == '__main__':
    host = '0.0.0.0' if platform.system() == 'Linux' else '127.0.0.1'
    uvicorn.run('dst_run.app.app:app',
                host=host,
                port=5800,
                reload=True)

