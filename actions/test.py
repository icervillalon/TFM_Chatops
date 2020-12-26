import jenkins
import time

def _get_server_client():
    server = jenkins.Jenkins('http://localhost:8080', username='admin', password='1234')
    return server

def _get_last_completed_job_info(jenkins_server, job_name):
    last_build_number = jenkins_server.get_job_info(job_name)['lastCompletedBuild']['number']
    get_build_console_output = jenkins_server.get_build_console_output(job_name, last_build_number)
    return get_build_console_output

def _get_current_execution_result(jenkins_server, job_name):
    current_number_execution = jenkins_server.get_job_info(job_name)['nextBuildNumber']
    return current_number_execution

def _get_job_results(jenkins_server, job_name, job_number):
    counter_var = 0
    while job_number != jenkins_server.get_job_info(job_name)['lastBuild']['number']:
        # Prevent the log to be flooded
        if counter_var % 2 == 0:
            print('Waiting for Jenkins build, please wait...')
        time.sleep(3)
        counter_var += 1
    console_output = jenkins_server.get_build_console_output(job_name, job_number)
    return console_output

if __name__=='__main__':
    jenkins_instance = _get_server_client()
    jenkins_instance.build_job('get_package_list')
    print(_get_job_results(jenkins_instance,'get_package_list',_get_current_execution_result(jenkins_instance,'get_package_list')))