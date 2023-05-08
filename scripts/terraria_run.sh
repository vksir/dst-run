#!/usr/bin/env bash

set -e

INSTALL_DIR="${HOME}/neutron-star/dst-run"

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

function print_help() {
    echo \
"Terraria Run Script

Options:
  --install         [ steamcmd || tmodloader]
  --update          [ tmodloader ]
  --start           [ tmodloader ]
  --install-mod     Prepare ~/neutron-star/dst-run/install.txt
                            ~/neutron-star/dst-run/enable.json
                            ~/neutron-star/dst-run/serverconfig.txt
  -h|--help
  --update-script
"
}

function update_script() {
    # TODO
    exit 0
}

function install_steamcmd() {
    sudo apt update \
    && sudo apt install software-properties-common -y \
    && sudo add-apt-repository multiverse \
    && sudo dpkg --add-architecture i386 \
    && sudo apt update \
    && sudo apt install lib32gcc1 steamcmd -y
}

function install_tmodloader() {
    mkdir -p "${INSTALL_DIR}" && cd "${INSTALL_DIR}" || exit 1
    curl -OL https://raw.githubusercontent.com/tModLoader/tModLoader/1.4/patches/tModLoader/Terraria/release_extras/DedicatedServerUtils/manage-tModLoaderServer.sh
    chmod 755 ./manage-tModLoaderServer.sh
    rm -rf ./tModLoader
    ./manage-tModLoaderServer.sh --install --github --folder ./tModLoader

    cd ./tModLoader || exit 1
    # Exit before start server
    sed -i "s/.*tModLoader.dll.*/exit 0\n/g" ./LaunchUtils/ScriptCaller.sh
    # Fix nosteam not working
    sed -i "s/.*steam_server}+x.*/if [ -z \"\${steam_server}\" ]; then/g" ./start-tModLoaderServer.sh

    chmod 755 start-tModLoaderServer.sh
    ./start-tModLoaderServer.sh -nosteam
}

function update_tmodloader() {
    cd "${INSTALL_DIR}" || exit 1
    ./manage-tModLoaderServer.sh --update --github --folder ./tModLoader
}

function start_tmodloader() {
    cd "${INSTALL_DIR}/tModLoader" || exit 1
    ./dotnet/6.0.0/dotnet tModLoader.dll -server -config serverconfig.txt
}

function install_mod() {
    cd "${INSTALL_DIR}" || exit 1
    ./manage-tModLoaderServer.sh --install --github --folder ./tModLoader --mods-only 
}

# Check args
if (($# == 0)); then
	print_err "No arguments supplied"
	print_help
	exit 1
fi

# Load args
while (($# > 0)); do
	case $1 in
		-h|--help)
			print_help
			exit 0
			;;
		--update-script)
            update_script
			exit 0
			;;
		--install)
			install="$2"
			shift; shift
			;;
		--update)
			update="$2"
			shift; shift
			;;
		--start)
			start="$2"
			shift; shift
			;;
		--install-mod)
            install_mod
			exit 0
			;;
		*)
			print_err "Argument not recognized: $1"
			print_help
			exit 1
			;;
	esac
done

# Execute
if [ -n "${install}" ]; then
    if [ "${install}" == "steamcmd" ]; then
        install_steamcmd
	elif [ "${install}" == "tmodloader" ]; then
	    install_tmodloader
	fi
elif [ -n "${update}" ]; then
	if [ "${update}" == "tmodloader" ]; then
	    update_tmodloader
	fi
elif [ -n "${start}" ]; then
	if [ "${start}" == "tmodloader" ]; then
	    start_tmodloader
	fi
fi
