echo "Setting up Planner for Docker..."
sh container-build.sh
sh compose.sh

#might work only on debian?
docker exec -it Planner_Webserver /bin/bash -c "ln -snf /usr/share/zoneinfo/Europe/Berlin /etc/localtime && dpkg-reconfigure -f noninteractive tzdata"