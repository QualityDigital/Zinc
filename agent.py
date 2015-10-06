import time
import sys
from nexus import Nexus

class Agent(object):
    def __init__(self, actions_file):
        with open(actions_file, 'rt') as actions:
            self.actions = {}
            for action in actions:
                action = action.strip()
                action_fields = action.split("  ")
                self.actions[action_fields[0]] = action_fields[1:]

    def execute_suite(self, case_file):
        cases = sys.argv[1]
        browsers = sys.argv[2]
        hubs = sys.argv[3]
        targets = sys.argv[4]
        screenshot = sys.argv[5]
        include = sys.argv[6]
        at = sys.argv[7]
        view_delay = sys.argv[8]
        pause_point, pause_delay = sys.argv[9].split("=")

        if include == "Y":
            cases = cases.split(",")
            for case in cases:
                self.execute_case(case, browsers, hubs, targets, screenshot, case_file, at, view_delay, pause_point, pause_delay)

    def execute_case(self, suite_case, suite_browsers, suite_hubs, suite_targets, suite_screenshot, case_file, at, view_delay, pause_point, pause_delay):
        case_browsers = suite_browsers.split(",")
        case_hubs = suite_hubs.split(",")
        case_targets = suite_targets.split(",")
        for case_browser in case_browsers:
            for case_hub in case_hubs:
                for case_target in case_targets:
                    with open(case_file, 'rt') as cases:
                        for case in cases:
                            case = case.strip()
                            case_fields = case.split("  ")
                            case_identifier, case_description, explicit_wait, case_actions = case_fields
                            if case_identifier == suite_case:
                                self.run_test(case_identifier, case_description, explicit_wait, case_actions, case_browser, case_hub, case_target, suite_screenshot, at, view_delay, pause_point, pause_delay)

    def run_test(self, case_identifier, case_description, explicit_wait, case_actions, case_browser, case_hub, case_target, action_screenshot, at, view_delay, pause_point, pause_delay):
        nexus = Nexus(case_browser, case_hub, case_target, case_identifier)
        journey_actions = case_actions.split(",")

        print("Executing \"{0} :: {1}\"\n".format(case_identifier, case_description))

        for count, journey_action in enumerate(journey_actions, start=1):
            action_type, action_on, action_by, action_text, action_description = self.actions[journey_action]
            result = nexus.execute_test(explicit_wait, journey_action, action_type, action_on, action_by, action_text, action_screenshot, at, count, view_delay, pause_point, pause_delay)
            print("{:<2}. {}\n\033[34m{}\033[0m\n".format(count, action_description, result))
            if format(pause_point) == format(count):
                if format(pause_delay) != "0":
                    print("Paused at step " + format(count) + " for " + format(pause_delay) + " seconds.\n")
                    time.sleep(float(pause_delay))

if __name__ == "__main__":
    start_time = time.time()
    agent = Agent('actions')
    agent.execute_suite('cases')

    print("-------------------------------")
    elapsed_time = (time.time() - start_time)
    if elapsed_time < 120.0:
        print("    Duration: {0:.2f} seconds".format(elapsed_time))
    else:
        print("    Duration: {0:.2f} minutes".format(elapsed_time/60))
    print("-------------------------------")
