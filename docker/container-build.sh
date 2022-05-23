echo "Rebuilding Docker containers..."

rebuild_image () {
    echo "Removing image $1"
    docker image remove "$1"
    echo "Building image $1"
    docker build --tag "$1" $2
}

#To rebuild containers here
#args: containerTag, buildpath
rebuild_image "planner-server:latest" "../"