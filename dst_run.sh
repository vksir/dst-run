#!/bin/bash

steamcmd_dir="$HOME/steamcmd"
dst_dir="$HOME/dst"
cluster_name="Cluster_1"
cluster_dir="$HOME/.klei/DoNotStarveTogether"

set_mod()
{
    # 生成 mod 安装文件
    python3 ./mod_update.py \
        "${cluster_dir}/${cluster_name}/Master/modoverrides.lua" \
        "${dst_dir}/mods/dedicated_server_mods_setup.lua"

    # 保证 Master 和 Cave 的 mod 文件一致
    cp "${cluster_dir}/${cluster_name}/Master/modoverrides.lua" \
        "${cluster_dir}/${cluster_name}/Caves/modoverrides.lua"
}
get_run_shared()
{
    cd "$dst_dir/bin64"

    run_shared=(./dontstarve_dedicated_server_nullrenderer_x64)
    run_shared+=(-console)
    run_shared+=(-cluster $cluster_name)
    run_shared+=(-monitor_parent_process $$)
}

echo "What to do? (Ver1.1.1/By Villkiss)"
echo "--------- Vanilla ---------"
echo "  (1) Run"
echo "  (2) Update and Run"
echo "  (3) Add Mods"
echo "--------- Other ---------"
echo "  (4) Install dependencies"
echo "  (5) Install SteamCMD"
echo "  (6) Install\Update DST_server"
echo "  (7) Run Cutstom"
echo "  (8) Run Dev"
echo "  (9) Edit Mods File"
echo "  (10) Exit"
read chose
if [ $chose == "1" ]
then
    set_mod
    get_run_shared
    "${run_shared[@]}" -shard Caves  | sed 's/^/Caves:  /' &
    "${run_shared[@]}" -shard Master | sed 's/^/Master: /'
elif [ $chose == "2" ]      # Update and Run
then
    $steamcmd_dir/steamcmd.sh +force_install_dir $dst_dir +login anonymous +app_update 343050 validate +quit
    set_mod
    get_run_shared
    "${run_shared[@]}" -shard Caves  | sed 's/^/Caves:  /' &
    "${run_shared[@]}" -shard Master | sed 's/^/Master: /'
elif [ $chose == "3" ]      # Add Mods
then
    clear
    echo "Which kind of mods to add?"
    echo "  (1) Modoverrides"
    echo "  (2) Mod ID"
    echo "  (3) Exit"
    read chose
    if [ $chose == "1" ]
    then
        echo "Print Modoverrides:"
        python3 ./mod_add.py "${cluster_dir}/${cluster_name}/Master/modoverrides.lua" "modoverrides"
        set_mod
        echo "Add success."
    elif [ $chose == "2" ]
    then
        echo "Print Mod ID:"
        python3 ./mod_add.py "${cluster_dir}/${cluster_name}/Master/modoverrides.lua" "modid"
        set_mod
        echo "Add success."
    elif [ $chose == "3" ]     # Exit
    then
        echo "Exit."
    else
        echo "Command Error."
    fi
elif [ $chose == "4" ]      # Install dependencies
then
    add-apt-repository multiverse
    dpkg --add-architecture i386
    apt update
    apt install lib32gcc1 steamcmd
    apt install libstdc++6:i386 libgcc1:i386 libcurl4-gnutls-dev:i386 -y
elif [ $chose == "5" ]      # Install SteamCMD
then
    mkdir -p ~/steamcmd/
    cd ~/steamcmd/
    wget "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz"
    tar -xvzf steamcmd_linux.tar.gz
    rm steamcmd_linux.tar.gz
elif [ $chose == "6" ]      # Install\Update DST_server
then
    $steamcmd_dir/steamcmd.sh +force_install_dir $dst_dir +login anonymous +app_update 343050 validate +quit
elif [ $chose == "7" ]     # Run Custom
then
    clear
    echo "Which to run?"
    echo "  (1) MyDediServer2"
    echo "  (2) Single_world"
    echo "  (3) Reforged"
    echo "  (4) Exit"
    read chose
    if [ $chose == "1" ]
    then
        cluster_name="MyDediServer2"
        set_mod
        get_run_shared
        "${run_shared[@]}" -shard Caves  | sed 's/^/Caves:  /' &
        "${run_shared[@]}" -shard Master | sed 's/^/Master: /'
    elif [ $chose == "2" ]
    then
        set_mod
        get_run_shared
        "${run_shared[@]}" -shard Master | sed 's/^/Master: /'
    elif [ $chose == "3" ]
    then
        cluster_name="Reforged"
        set_mod
        get_run_shared
        "${run_shared[@]}" -shard Master | sed 's/^/Master: /'
    elif [ $chose == "4" ]
    then
        echo "Exit."
    else
        echo "Command Error."
    fi
elif [ $chose == "8" ]     # Run Dev
then
    dst_dir="$HOME/dst_dev"
    cluster_dir="$HOME/.klei/DoNotStarveTogetherReturnOfThemBeta"

    clear
    echo "What to do with Dev Version?"
    echo "  (1) Run"
    echo "  (2) Install/Update DST_dev_server"
    echo "  (3) Exit"
    read chose
    if [ $chose == "1" ]
    then
        set_mod
        get_run_shared
        "${run_shared[@]}" -shard Caves  | sed 's/^/Caves:  /' &
        "${run_shared[@]}" -shard Master | sed 's/^/Master: /'
    elif [ $chose == "2" ]
    then
       $steamcmd_dir/steamcmd.sh +force_install_dir $dst_dir +login anonymous +app_update 343050 validate -beta returnofthembeta +quit
    elif [ $chose == "3" ]
    then
        echo "Exit."
    else
        echo "Command Error."
    fi
elif [ $chose == "9" ]     # Exit
then
    vim "${cluster_dir}/${cluster_name}/Master/modoverrides.lua"
elif [ $chose == "10" ]
then
    echo "Exit."
else
    echo "Command Error."
fi


