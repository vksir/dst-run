#!/usr/bin/env bash

action="${1}"

ALLOWED_ACTION_ARGS=("run" "install" "uninstall" "upgrade")
REPO_URL="https://github.com/vksir/dst-run.git"
PROCESS_DIR="/etc/dst_run"
DST_RUN_CMD_PATH="${PROCESS_DIR}/scripts/setup.sh"
DST_RUN_SERVICE_PATH="${PROCESS_DIR}/configs/dstrun.service"
REQUIREMENTS_PATH="${PROCESS_DIR}/requirements.txt"



function print_ok() {
    local msg="${1}"
    echo "${msg}"
}

function print_err() {
    local msg="${1}"
    echo "${msg}" > /dev/stderr
}

function contain() {
    local list="${1}"
    local ele="${2}"
    for i in ${list[*]};
    do
        if [ "${ele}" == "${i}" ]; then
            return 0
        fi
    done
    return 1
}

function check_action_arg() {
    if ! contain "${ALLOWED_ACTION_ARGS[*]}" "${action}"; then
        echo "Action arg must be [ run || install || uninstall || upgrade ]"
        return 1
    fi
}

function run() {
    cd "${PROCESS_DIR}" && gunicorn dst_run.app.app:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5800
}

function setup() {
    if ! pip install -r "${REQUIREMENTS_PATH}"; then
        print_err "Install requirements failed"
        return 1
    fi
    if ! (chmod 755 "${DST_RUN_CMD_PATH}" && ln -fs "${DST_RUN_CMD_PATH}" /usr/bin/dstrun); then
        print_err "Generate dst-run soft link failed"
        return 1
    fi
    if ! (ln -fs "${DST_RUN_SERVICE_PATH}" /etc/systemd/system/dstrun.service && systemctl daemon-reload); then
        print_err "Generate dst-run service failed"
        return 1
    fi
    print_ok "Setup dst-run success"
}

function download () {
    if ! (rm -rf "${PROCESS_DIR}" && git clone "${REPO_URL}" "${PROCESS_DIR}"); then
        print_err "Download dst-run repo failed"
        return 1
    fi
    print_ok "Download dst-run success"
}

function uninstall() {
    if ! (rm -rf "${PROCESS_DIR}" && rm -f /usr/bin/dstrun && rm -f /etc/systemd/system/dstrun.service && systemctl daemon-reload); then
        print_err "Uninstall dst-run failed"
        return 1
    fi
    print_ok "Uninstall dst-run success"
}

function update() {
    if ! cd "${PROCESS_DIR}" && git pull; then
        print_err "Upgrade dst-run failed"
        return 1
    fi
    print_ok "Update dst-run success"
}


if ! check_action_arg; then
    exit 1
fi

if [ "${action}" == "run" ]; then
    run
elif [ "${action}" == "install" ]; then
    download && setup
elif [ "${action}" == "uninstall" ]; then
    uninstall
elif [ "${action}" == "upgrade" ]; then
    update && setup
fi

exit $?
