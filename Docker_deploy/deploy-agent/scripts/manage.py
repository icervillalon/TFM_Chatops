# Modify to Client instead of APIClient?
from docker import Client
import json
import tarfile
import os

import argparse

GITUSER = 'icervillalon'
TOKEN = 'FK8YN8QUkksGV6s2Sz69'
'''
Expected workflow:
-> Get from GIT the dockerfile of the updated service + the HTML document of the page
-> Deletes older docker images if there are any
-> Build the new docker image
-> Run the container with the new image in one port or another, depending on the environment
'''
DEPLOY_MODES = ['init', 'remove_server', 'update_packages', 'get_from_git', 'install_package', 'delete_package', 'get_packages']
# Parser for arguments at script launch
def _argument_parser():
    parser = argparse.ArgumentParser()
    # Add long and short argument
    parser.add_argument("--mode", "-m", help="set deployment mode")
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

'''
# Function to append datetime to html page after building
def _append_datetime(deploy_env):
    f = open('/home/jenkins/httpd_server/{}/public-html/index.html'.format(deploy_env), 'a+')
    f.write('Image build time: ' + str(datetime.now()))
    f.close()
    # Debug print file content
    f_r = open('/home/jenkins/httpd_server/{}/public-html/index.html'.format(deploy_env), 'r').read()
    print('Index content: ' + f_r)
'''

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
def execute_commands(client, command):
    # Get the ID of the container
    container_id = _get_container_id(client)
    if container_id != 'NONE':
        # Create exec instance
        exec_id = client.exec_create(container_id, command)
        # Launch exec
        command_result = client.exec_start(exec_id)
        if type(command_result)==None.__class__:
            command_result = '\n'
    else:
        command_result = 'Container not found. {} was not launched'.format(command)
    return command_result

def send_file(client, source_file, dest_path):
    # container object
    container = client.containers.get("development-server")

    os.chdir(os.path.dirname(source_file))
    srcname = os.path.basename(source_file)
    tar = tarfile.open(source_file + '.tar', mode='w')
    try:
        tar.add(srcname)
    finally:
        tar.close()

    data = open(source_file + '.tar', 'rb').read()
    container.put_archive(os.path.dirname(dest_path), data)
    print('Added file ' + dest_path)


# TODO:
# - Git integration to get the files? Check from Jenkins
# - Return messages to get catched by Jenkins and RASA
# -

if __name__ == '__main__':
    cli = Client(base_url='unix://var/run/docker.sock')
    # Argument parsing
    args = _argument_parser()
    deploy_mode = args.mode
    if deploy_mode == 'install_package' or deploy_mode == 'delete_package':
        package = args.package

    if deploy_mode == 'init':
        # Cleanup older images
        delete_image(cli)
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
        print(execute_commands(cli, 'bash -c "cd /home/developer"')).decode('utf-8')
        print(execute_commands(cli, 'git clone -n http://{}:{}@lab.gsi.upm.es/TFM/tfm-ignaciocervantes.git --depth 1'.format(GITUSER,TOKEN))).decode('utf-8')
        print(execute_commands(cli, 'bash -c "cd tfm-ignaciocervantes"')).decode('utf-8')
        print(execute_commands(cli, 'git checkout HEAD requirements.txt')).decode('utf-8')
        print(execute_commands(cli, 'pip install -r requirements.txt')).decode('utf-8')
        print('Successfully installed packages from GitLab')
    elif deploy_mode == 'install_package':
        print(execute_commands(cli, 'pip install {}'.format(package)).decode('utf-8'))
    elif deploy_mode == 'delete_package':
        print(execute_commands(cli, 'pip uninstall -y {}'.format(package)).decode('utf-8'))
    elif deploy_mode == 'get_packages':
        print(execute_commands(cli, 'pip freeze').decode('utf-8'))
    elif deploy_mode == 'copy_file':
        send_file(cli, 'requirements.txt', 'requirements.txt')
    else:
        print('Unsupported mode {}'.format(deploy_mode))
