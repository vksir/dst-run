#!/bin/bash


action="${1}"

function check_args() {
    echo "${action}" | grep -E 'run|install' > /dev/null
    if (($? != 0)); then
        echo "Args must be [ run || install ]"
        exit 1
    fi
}


function run() {
    uvicorn --host 0.0.0.0 --port 5800 --reload dst_run.app.app:app
}

function main() {
    check_args
    if [[ "${action}" == "run" ]]; then
        run
    fi
}

main
exit 0