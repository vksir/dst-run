# dst_run

## Install

```shell
curl -OL https://raw.githubusercontent.com/vksir/dst-run/master/scripts/setup.sh && bash setup.sh install
```

## Run

```shell
systemctl start dstrun
```

## Swag

```shell
swag init -g ./internal/server/server.go -o ./docs/ -p snakecase
```