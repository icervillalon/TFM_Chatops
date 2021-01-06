import jenkins

server = jenkins.Jenkins('http://localhost:8080', username='admin', password='1234')
print(server.get_build_console_output('install_package', server.get_job_info('get_package_list')['lastCompletedBuild']['number']))