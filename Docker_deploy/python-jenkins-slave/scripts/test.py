# Modify to Client instead of APIClient?
from docker import APIClient

'''
Expected workflow:
-> Get from GIT the dockerfile of the updated service + the HTML document of the page
-> Build the docker image
-> Run the container with the new image in one port or another, depending on the environment
-> Cleanup images after 
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
    return 0

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

# TODO:
# - Git integration to get the files? Check from Jenkins
# - Return messages to get catched by Jenkins and RASA
# -

if __name__ == '__main__':
    cli = APIClient(base_url='unix://var/run/docker.sock')

'''
## Testing code
cli = APIClient(base_url='unix://var/run/docker.sock')
container = cli.create_container(image='busybox:latest', command='/bin/sleep 30')
print(container)
print('Run container')
response = cli.start(container=container.get('Id'))
print(response)
'''
