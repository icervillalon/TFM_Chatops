# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"


import jenkins
import re
import time
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


def _get_server_client():
    server = jenkins.Jenkins('http://localhost:8080', username='admin', password='1234')
    return server

def _launch_jenkins_job(job_name, params={}):
    jenkins_instance = _get_server_client()
    if params:
        jenkins_instance.build_job(job_name, parameters=params)
    else:
        jenkins_instance.build_job(job_name)

def _get_last_completed_job_info(jenkins_server, job_name):
    last_build_number = jenkins_server.get_job_info(job_name)['lastCompletedBuild']['number']
    get_build_console_output = jenkins_server.get_build_console_output(job_name, last_build_number)
    return get_build_console_output

def _get_current_execution_number(jenkins_server, job_name):
    current_number_execution = jenkins_server.get_job_info(job_name)['nextBuildNumber']
    return current_number_execution

def _get_job_results(jenkins_server, job_name, job_number):
    counter_var = 0
    while job_number != jenkins_server.get_job_info(job_name)['lastCompletedBuild']['number']:
        time.sleep(1)
        # Count the seconds elapsed per action
        counter_var += 1
    print('Finished action. Time elapsed: ' + str(counter_var))
    console_output_raw = jenkins_server.get_build_console_output(job_name, job_number)
    console_output = _process_console_output(console_output_raw)
    return console_output

def _process_console_output(console_output):
    console_lines = console_output.split('\n')
    while console_lines:
        popped_line = console_lines.pop(0)
        if re.search('\+ sudo python', str(popped_line)) is not None:
            break
    console_clean_output = '\n'.join(console_lines).replace('Finished: SUCCESS', '').rstrip()
    return console_clean_output

class action_inform_user(Action):
    def name(self) -> Text:
        return "action_inform_user"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        last_intent = tracker.latest_message['intent'].get('name')
        if last_intent == 'server_state':
            message = 'Checking server state...'
        elif last_intent == 'launch_server':
            message = 'Launching the server instance, this may take a while...'
        elif last_intent == 'remove_server':
            message = 'Removing the server instance, please stand by!'
        elif last_intent == 'install_package':
            message = 'Installing the requested package...'
        elif last_intent == 'delete_package':
            message = 'Deleting the requested package...'
        elif last_intent == 'list_package':
            message = 'Listing the installed packages, please stand by...'
        elif last_intent == 'update_packages':
            message = 'Updating the packages, this may take a while...'
        elif last_intent == 'get_from_git':
            message = 'Updating the packages from git, please stand by!'
        else:
            message = 'Unknown intent!'
        dispatcher.utter_message(text=message)

        return []


class action_send_confirmation(Action):

    def name(self) -> Text:
        return "action_send_confirmation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        last_intent = tracker.latest_message['intent'].get('name')
        print('Accesed the action ' + self.name())
        if 'package' in last_intent:
            package_name = next(tracker.get_latest_entity_values('package'), None)
            dispatcher.utter_message(text="Intent detected: {}. Do you want to install {}".format(last_intent, package_name))
        else:
            dispatcher.utter_message(text="Intent detected: {}. Please confirm to to launch the automatism".format(last_intent))
        dispatcher.utter_message(buttons = [
            {"payload": "/affirm", "title": "Yes"},
            {"payload": "/deny", "title": "No"},
        ])

        return []


class action_server_state(Action):

    def name(self) -> Text:
        return "action_server_state"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        jenkins_server = _get_server_client()
        job_name = 'check_server_state'
        print('Accesed the action ' + self.name())

        current_job = _get_current_execution_number(jenkins_server, job_name)
        _launch_jenkins_job(job_name)
        job_console_results = _get_job_results(jenkins_server, job_name, current_job)
        dispatcher.utter_message(job_console_results)

        return []


class action_launch_server(Action):

    def name(self) -> Text:
        return "action_launch_server"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        jenkins_server = _get_server_client()
        job_name = 'deploy_server'
        print('Accesed the action ' + self.name())

        current_job = _get_current_execution_number(jenkins_server, job_name)
        _launch_jenkins_job(job_name)
        job_console_results = _get_job_results(jenkins_server, job_name, current_job)
        dispatcher.utter_message(text="Execution finished! Console output:\n" + job_console_results)

        return []


class action_remove_server(Action):

    def name(self) -> Text:
        return "action_remove_server"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print('Accesed the action ' + self.name())
        dispatcher.utter_message(text="Launched "+ self.name())

        return []


class action_install_package(Action):

    def name(self) -> Text:
        return "action_install_package"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        parameters = {'PACKAGE': next(tracker.get_latest_entity_values('package'), None)}
        if parameters['PACKAGE'] is not None:
            jenkins_server = _get_server_client()
            job_name = 'install_package'
            print('Accesed the action ' + self.name() + ' with the entity ' + parameters['PACKAGE'])

            current_job = _get_current_execution_number(jenkins_server, job_name)
            _launch_jenkins_job(job_name, parameters)
            job_console_results = _get_job_results(jenkins_server, job_name, current_job)
            dispatcher.utter_message(text="Execution finished! Console output:\n" + job_console_results)
        else:
            dispatcher.utter_message("You tried to install a package? Sorry, I didn't got which one! Can you use the format \"package==1.0.0\" to specify the version?")


        return []


class action_delete_package(Action):

    def name(self) -> Text:
        return "action_delete_package"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        parameters = {'PACKAGE': next(tracker.get_latest_entity_values('package'), None)}
        if parameters['PACKAGE'] is not None:
            jenkins_server = _get_server_client()
            job_name = 'delete_package'
            print('Accesed the action ' + self.name() + ' with the entity ' + parameters['PACKAGE'])

            current_job = _get_current_execution_number(jenkins_server, job_name)
            _launch_jenkins_job(job_name, parameters)
            job_console_results = _get_job_results(jenkins_server, job_name, current_job)
            dispatcher.utter_message(text="Execution finished! Console output:\n" + job_console_results)
        else:
            dispatcher.utter_message("You tried to delete a package? Sorry, I didn't got which one! Can you use the format \"package==1.0.0\" to specify the version?")

        return []


class action_list_package(Action):

    def name(self) -> Text:
        return "action_list_package"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        jenkins_server = _get_server_client()
        job_name = 'get_package_list'
        print('Accesed the action ' + self.name())

        current_job = _get_current_execution_number(jenkins_server, job_name)
        _launch_jenkins_job(job_name)
        job_console_results = _get_job_results(jenkins_server, job_name, current_job)
        dispatcher.utter_message(text="Packages installed:\n" + job_console_results)

        return []


class action_update_package(Action):

    def name(self) -> Text:
        return "action_update_packages"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print('Accesed the action ' + self.name())
        dispatcher.utter_message(text="Launched "+ self.name())

        return []


class action_get_from_git(Action):

    def name(self) -> Text:
        return "action_get_from_git"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print('Accesed the action ' + self.name())
        dispatcher.utter_message(text="Launched "+ self.name())

        return []
