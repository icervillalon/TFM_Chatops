# Modify to Client instead of APIClient?
from docker import APIClient

import argparse

'''
Expected workflow:
-> Get from GIT the dockerfile of the updated service + the HTML document of the page
-> Deletes older docker images if there are any
-> Build the new docker image
-> Run the container with the new image in one port or another, depending on the environment
'''
# Generates a docker image from a provided dockerfile
def build_image(client, dockerfile_path, deploy_env):
    response = [line for line in client.build(
        path=dockerfile_path, rm = True, tag='httpd_server_{}'.format(deploy_env.upper())
    )]
    # Format of last response line expected: {"stream":"Successfully built 032b8b2855fc\\n"}
    if 'Succesfully' in response[-1]['stream']:
        return 0
    else:
        print('DEBUG! Error found: ' + response[-1]['stream'])
        return 1

# Creates and runs a docker container
def run_container(client, deploy_env):
    # Determine the port for each environment
    if deploy_env == 'PRO':
        exposed_port = 8088
    elif deploy_env == 'PRE':
        exposed_port = 8089

    container = client.create_container(
        image='httpd_server_{}'.format(deploy_env.upper()),
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
    if running_container:
        client.kill(running_container)
        client.remove_container(running_container)
        return 0
    else:
        raise Exception('Could not find the container httpd-server-{}. Execution aborted.'.format(deploy_env))

# Returns the ID of a container if it's running. If it can't be find, return False
def _get_container_id(client, deploy_env):
    found_container = False
    for container in client.containers():
        if 'httpd-server-{}'.format(deploy_env) in container['Image']:
            found_container = True
            running_container = container['Id']
    if not found_container:
        running_container = False
    return running_container

# Parser for arguments at script launch
def _argument_parser():
    parser = argparse.ArgumentParser()
    # Add long and short argument
    parser.add_argument("--env", "-e", help="set deploy environment")
    # Read arguments from the command line
    args = parser.parse_args()
    return args

# Deletes the existing image of a container
def delete_image(client, deploy_env):
    if _get_container_id(client, deploy_env):
        client.remove_image('httpd-server-{}'.format(deploy_env))
    else:
        remove_previous_instance(client,deploy_env)
        client.remove_image('httpd-server-{}'.format(deploy_env))

# TODO:
# - Git integration to get the files? Check from Jenkins
# - Return messages to get catched by Jenkins and RASA
# -

if __name__ == '__main__':
    args = _argument_parser()
    deploy_env = args.env
    cli = APIClient(base_url='unix://var/run/docker.sock')

    # Cleanup older images
    delete_image(cli, deploy_env)
    # Build new images
    build_image(cli, '/path/to/httpd_dockerfile', deploy_env)
    # Create and run new container
    result, exposed_port = run_container(cli, deploy_env)
    print('Created container with the image httpd-server-{} at port {}'.format(deploy_env, str(exposed_port)))


'''
## Testing code
cli = APIClient(base_url='unix://var/run/docker.sock')
container = cli.create_container(image='busybox:latest', command='/bin/sleep 30')
print(container)
print('Run container')
response = cli.start(container=container.get('Id'))
print(response)
'''