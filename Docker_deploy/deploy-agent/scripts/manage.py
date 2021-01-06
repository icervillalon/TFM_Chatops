# Modify to Client instead of APIClient?
from docker import Client
import json
import argparse

# Parser for arguments at script launch
def _argument_parser():
    parser = argparse.ArgumentParser()
    # Add long and short argument
    parser.add_argument("--mode", "-m", help="set command mode")
    parser.add_argument("--package", "-p", help="package name")
    # Read arguments from the command line
    args = parser.parse_args()
    return args


# Returns the ID of a container if it's running. If it can't be find, return False
def _get_container_id(client):
    for container in client.containers():
        if 'development-server' in container['Image']:
            found_container = True
            running_container = container['Id']
            return running_container
    running_container = 'NONE'
    return running_container

# Returns true or false if the image for the given environment exists
def _get_image(client):
    image_name = 'development-server'
    if image_name in str(json.dumps(client.images())):
        print(image_name + ' image found')
        return True
    else:
        print(image_name + ' image not found')
        return False

# Generates a docker image from a provided dockerfile
def build_image(client, dockerfile_path):
    # Append the datetime of the last build
    # _append_datetime(deploy_env)
    # Build the image
    print('Building image, this may take some time...')
    response = [line for line in client.build(
        path=dockerfile_path, rm=True, tag='development-server'
    )]
    # Format of last response line expected: {"stream":"Successfully built 032b8b2855fc\\n"}
    print('Dockerfile build result: ' + str(response[-1].decode('utf-8')))

# Creates and runs a docker container
def run_container(client):
    # Export port for ssh
    exposed_port = 22000

    container = client.create_container(
        image='development-server',
        name='development-server',
        detach=True,
        ports=[22],
        host_config=cli.create_host_config(port_bindings={
            22:exposed_port
        })
    )
    client.start(container=container.get('Id'))
    return 0, exposed_port

# Stops and removes a container
def remove_previous_instance(client):
    running_container = _get_container_id(client)
    if running_container != 'NONE':
        print('Killing local container')
        client.kill(running_container)
        print('Removing container')
        client.remove_container(running_container)
        return 0
    else:
        print('No previous containers found.')

# Deletes the existing image of a container
def delete_image(client):
    if _get_image(client):
        if _get_container_id(client) == 'NONE':
            print('No running containers found, deleting image...')
            client.remove_image('development-server')
        else:
            print('Found running containers, deleting image...')
            remove_previous_instance(client)
            client.remove_image('development-server')
        print('Image succesfully deleted')
        return True
    else:
        print('Image "development-server" not found')
        return False

# Execute commands towards the development server
def execute_commands(client, command, workdir=''):
    # Get the ID of the container
    container_id = _get_container_id(client)
    if container_id != 'NONE':
        # Create exec instance with a directory if it is passed.
        if workdir:
            exec_id = client.exec_create(container_id, command, workdir=workdir)
        else:
            exec_id = client.exec_create(container_id, command)
        # Launch exec
        command_result = client.exec_start(exec_id)
    else:
        command_result = 'Container not found. {} was not launched'.format(command)
    return command_result

if __name__ == '__main__':
    cli = Client(base_url='unix://var/run/docker.sock')
    # Argument parsing
    args = _argument_parser()
    deploy_mode = args.mode
    if deploy_mode == 'install_package' or deploy_mode == 'delete_package':
        package = args.package

    if deploy_mode == 'status':
        if _get_container_id(cli) != 'NONE':
            print('Development server is running!')
        else:
            print('Development server is not currently running.')
    elif deploy_mode == 'init':
        # Clean up older images
        #delete_image(cli)
        remove_previous_instance(cli)
        # Build new images
        build_image(cli, '/home/jenkins/development_server')
        # Create and run new container
        result, exposed_port = run_container(cli)
        print('Created container with the image development-server, exposing ssh at port {}'.format(str(exposed_port)))
    elif deploy_mode == 'remove_server':
        remove_previous_instance(cli)
        print('Removed development-server instance')
    elif deploy_mode == 'update_packages':
        print(execute_commands(cli, "pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U").decode('utf-8'))
    elif deploy_mode == 'get_from_git':
        print(execute_commands(cli, "sh bash_git_clone.sh", workdir='/home/developer'))
        print('Successfully installed packages from GitLab')
    elif deploy_mode == 'install_package':
        print(execute_commands(cli, 'pip install {}'.format(package)).decode('utf-8'))
    elif deploy_mode == 'delete_package':
        print(execute_commands(cli, 'pip uninstall -y {}'.format(package)).decode('utf-8'))
    elif deploy_mode == 'get_packages':
        print(execute_commands(cli, 'pip freeze').decode('utf-8'))
    else:
        print('Unsupported mode {}'.format(deploy_mode))
