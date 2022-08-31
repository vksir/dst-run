import uvicorn


def main():
    uvicorn.run('app.app:app',
                host='0.0.0.0',
                port=5800)


if __name__ == '__main__':
    main()
