# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionServerState(Action):

    def name(self) -> Text:
        return "action_server_state"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print('Accesed the action ' + self.name())
        dispatcher.utter_message(text="Launched "+ self.name())

        return []


class ActionLaunchServer(Action):

    def name(self) -> Text:
        return "action_launch_server"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print('Accesed the action ' + self.name())
        dispatcher.utter_message(text="Launched "+ self.name())

        return []


class ActionRemoveServer(Action):

    def name(self) -> Text:
        return "action_remove_server"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print('Accesed the action ' + self.name())
        dispatcher.utter_message(text="Launched "+ self.name())

        return []


class ActionInstallPackage(Action):

    def name(self) -> Text:
        return "action_install_package"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print(str(tracker.last_message['entities']))
        package_name = next(tracker.get_latest_entity_values('package'), None)
        print('Accesed the action ' + self.name())
        dispatcher.utter_message(text="Launched "+ self.name() + " and caught entity " + package_name)

        return []


class ActionDeletePackage(Action):

    def name(self) -> Text:
        return "action_delete_package"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print(str(tracker.last_message['entities']))
        package_name = next(tracker.get_latest_entity_values('package'), None)
        print('Accesed the action ' + self.name())
        dispatcher.utter_message(text="Launched "+ self.name() + " and caught entity " + package_name)

        return []


class ActionListPackage(Action):

    def name(self) -> Text:
        return "action_list_package"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print('Accesed the action ' + self.name())
        dispatcher.utter_message(text="Launched "+ self.name())

        return []


class ActionUpdatePackages(Action):

    def name(self) -> Text:
        return "action_update_packages"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print('Accesed the action ' + self.name())
        dispatcher.utter_message(text="Launched "+ self.name())

        return []


class ActionGetFromGit(Action):

    def name(self) -> Text:
        return "action_get_from_git"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print('Accesed the action ' + self.name())
        dispatcher.utter_message(text="Launched "+ self.name())

        return []
