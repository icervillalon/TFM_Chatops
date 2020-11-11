from docker import Client

cli = Client(base_url='unix://var/run/docker.sock')
container = cli.create_container(image='busybox:latest', command='/bin/sleep 30')
print(container)
print('Run container')
response = cli.start(container=container.get('Id'))
print(response)