# Modify to Client instead of APIClient?
from docker import Client
import json
from datetime import datetime

import argparse

'''
Expected workflow:
-> Get from GIT the dockerfile of the updated service + the HTML document of the page
-> Deletes older docker images if there are any
-> Build the new docker image
-> Run the container with the new image in one port or another, depending on the environment
'''
# Parser for arguments at script launch
def _argument_parser():
    parser = argparse.ArgumentParser()
    # Add long and short argument
    parser.add_argument("--env", "-e", help="set deploy environment")
    # Read arguments from the command line
    args = parser.parse_args()
    return args

# Returns the ID of a container if it's running. If it can't be find, return False
def _get_container_id(client, deploy_env):
    for container in client.containers():
        if 'httpd-server-{}'.format(deploy_env) in container['Image']:
            found_container = True
            running_container = container['Id']
            return running_container
    running_container = 'NONE'
    return running_container

# Returns true or false if the image for the given environment exists
def _get_image(client, deploy_env):
    image_name = 'httpd-server-{}'.format(deploy_env)
    if image_name in str(json.dumps(client.images())):
        print(image_name + ' image found')
        return True
    else:
        print(image_name + ' image not found')
        return False

# Function to append datetime to html page after building
def _append_datetime(deploy_env):
    f = open('/home/jenkins/httpd_server/{}/public-html/index.html'.format(deploy_env), 'a+')
    f.write('Image build time: ' + str(datetime.now()))
    f.close()
    # Debug print file content
    f_r = open('/home/jenkins/httpd_server/{}/public-html/index.html'.format(deploy_env), 'r').read()
    print('Index content: ' + f_r)

# Generates a docker image from a provided dockerfile
def build_image(client, dockerfile_path, deploy_env):
    # Append the datetime of the last build
    _append_datetime(deploy_env)
    # Build the image
    response = [line for line in client.build(
        path=dockerfile_path, rm = True, tag='httpd-server-{}'.format(deploy_env)
    )]
    # Format of last response line expected: {"stream":"Successfully built 032b8b2855fc\\n"}
    print('Dockerfile build result: ' + str(response[-1].decode('utf-8')))

# Creates and runs a docker container
def run_container(client, deploy_env):
    deploy_env = deploy_env.lower()
    # Determine the port for each environment
    if deploy_env == 'pro':
        exposed_port = 8088
    elif deploy_env == 'pre':
        exposed_port = 8089
    else:
        raise Exception('Invalid deploy environment "{}". Execution aborted.'. format(deploy_env))

    container = client.create_container(
        image='httpd-server-{}'.format(deploy_env),
        name='httpd-server-{}'.format(deploy_env),
        detach=True,
        ports=[80],
        host_config=cli.create_host_config(port_bindings={
            80:exposed_port
        })
    )
    client.start(container=container.get('Id'))
    return 0, exposed_port

# Stops and removes a container
def remove_previous_instance(client, deploy_env):
    running_container = _get_container_id(client,deploy_env)
    if running_container != 'NONE':
        print('Killing local container')
        client.kill(running_container)
        print('Removing container')
        client.remove_container(running_container)
        return 0
    else:
        print('No previous containers found.')

# Deletes the existing image of a container
def delete_image(client, deploy_env):
    if _get_image(client, deploy_env):
        if _get_container_id(client, deploy_env) == 'NONE':
            print('No running containers found, deleting image...')
            client.remove_image('httpd-server-{}'.format(deploy_env))
        else:
            print('Found running containers, deleting image...')
            remove_previous_instance(client,deploy_env)
            client.remove_image('httpd-server-{}'.format(deploy_env))
        print('Image succesfully deleted')
        return True
    else:
        print('Image "httpd-server-{}" not found'.format(deploy_env))
        return False

# TODO:
# - Git integration to get the files? Check from Jenkins
# - Return messages to get catched by Jenkins and RASA
# -

if __name__ == '__main__':
    args = _argument_parser()
    deploy_env = args.env
    cli = Client(base_url='unix://var/run/docker.sock')

    # Cleanup older images
    delete_image(cli, deploy_env)
    # Build new images
    build_image(cli, '/home/jenkins/httpd_server/{}'.format(deploy_env), deploy_env)
    # Create and run new container
    result, exposed_port = run_container(cli, deploy_env)
    print('Created container with the image httpd-server-{} at port {}'.format(deploy_env, str(exposed_port)))
