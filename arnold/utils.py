import importlib
import logging
import string
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from arnold.constants import COMMAND_MAP, INT_MAP

_logger = logging.getLogger(__name__)


def sanitise_input(input: str, punctuation: Optional[str] = None) -> str:
    """
    Sanitise the input string by removing punctuation and converting to lowercase.
    """
    punctuation = punctuation or string.punctuation
    return input.translate(str.maketrans('', '', punctuation)).lower()


class InterruptibleDelay(object):
    """
    An interruptable delay used to ensure that `sleep` can be interrupted
    before the delay timeout is complete.

    Args:
        halt_callback (callable, optional): The function to call when the delay
        is interrupted or complete.

    """
    def __init__(self, halt_callback: Optional[Callable] = None) -> None:
        self.interrupt = False
        self.active = False
        self.halt_callback = halt_callback

    def delay(self, duration: int) -> None:
        """
        Sleep until the duration is up or interrupt if needed. Keeps active
        state and calls halt_callback prior to returning.

        Args:
            duration (int): The duration to sleep for
        """
        self.active = True
        count = 0
        while count < duration * 10:
            if self.interrupt:
                self.interrupt = False
                break
            time.sleep(0.1)
            count += 1
        self.halt_callback()
        self.active = False

    def async_delay(self, duration: int) -> None:
        """
        Calls delay in a thread and starts.

        Args:
            duration (int): The duration to sleep for
        """
        thread = threading.Thread(target=self.delay, args=(duration, ))
        thread.start()

    def is_active(self) -> bool:
        """
        Helper to return if the delay is active or not.

        Returns:
            bool: delay is active
        """
        return self.active

    def terminate(self) -> None:
        """
        Sets interrupt in order to terminate the delay.
        """
        self.interrupt = True


class CommandParser(object):
    """
    The `CommandParser` class is responsible for parsing a command string and executing
    the corresponding method based on a command mapping.

    Args:
        command (str): The command string to be parsed.
        command_map (dict, optional): The command mapping to be used for parsing the
        command. Defaults to None.
    """

    def __init__(self, command: str, command_map: Optional[Dict] = None) -> None:
        self.command = command
        self.command_parts = self._split_command()
        self.command_map = command_map or COMMAND_MAP

        # Setup logging
        self._logger = _logger

    def _split_command(self) -> List:
        """
        Remove all punctuation and split the command into words.

        Returns:
            list: command word list
        """
        clean_command = sanitise_input(self.command)
        return clean_command.split(' ')

    def _get_method(self, class_path: str, method_name: str) -> Tuple[object, Callable]:
        """Import and initiate the class and return the method.

        Args:
            class_path (str): the path to the class
            method_name (str): the method to return

        Returns:
            tuple (object, callable): the class instance and method the command
            is calling
        """
        class_path_list = class_path.split('.')
        class_name = class_path_list[-1]
        module_path = '.'.join(class_path_list[:-1])
        module = importlib.import_module(f'arnold.{module_path}')
        cls = getattr(module, class_name)
        instance = cls()
        return instance, getattr(instance, method_name)

    def _get_recognised_tokens(self, tokens: List) -> Set:
        """
        Get a set of recognised tokens.

        Args:
            tokens (list): list of command tokens that trigger a method

        Returns:
            set: set of recognised tokens
        """
        return set(self.command_parts).intersection(set(tokens))

    def _parse_command_map(self) -> Optional[Dict]:
        """
        Iterates over the command map and extractsthe matching class map.

        Returns:
            dict: class map
        """
        for command_map in self.command_map.values():
            recognised_class_token = self._get_recognised_tokens(
                tokens=command_map['tokens']
            )
            if recognised_class_token:
                return command_map['map']

    def _parse_class_map(self, class_map: Dict) -> Optional[Dict]:
        """
        Iterates over the class map and extracts the matching method map.

        Args:
            class_map (dict): class map to iterate over

        Returns:
            dict: method map
        """
        for method_map in class_map['methods']:
            recognised_method_token = self._get_recognised_tokens(
                tokens=method_map['tokens']
            )
            if recognised_method_token:
                return method_map

    def _get_method_params(self, method_map: Dict) -> Optional[Dict]:
        """
        Iterates over the method map and extracts the matching params and their
        values.

        Args:
            method_map (dict): method map to iterate over

        Returns:
            dict: params to invoke the method with
        """
        method_params = {}
        for param_map in method_map['params']:
            recognised_param_token = self._get_recognised_tokens(
                tokens=param_map['tokens']
            )
            if recognised_param_token:
                param_value = param_map['param_value']

                # Determine the param value if set to lookup value
                index_modifier = None
                if param_value == 'suffix':
                    index_modifier = 1
                elif param_value == 'prefix':
                    index_modifier = -1

                # Extract the param value based on the index modifier
                if index_modifier is not None:
                    value_index = (
                        self.command_parts.index(list(recognised_param_token)[0]) + index_modifier
                    )
                    param_value = self.command_parts[value_index]
                    if param_value in INT_MAP:
                        param_value = INT_MAP[param_value]
                    else:
                        try:
                            param_value = int(param_value)
                        except TypeError:
                            pass

                method_params.update({
                    param_map['param']: param_value
                })

        return method_params

    def parse(self) -> Any:
        """Parse the command based on the command mapping and execute the
        required method.

        Returns:
            any: the result of the executed method
        """
        class_map = self._parse_command_map()
        if class_map is not None:
            method_map = self._parse_class_map(class_map)
            if method_map is not None:
                class_path = class_map['class']
                method_name = method_map['method']
                instance, method = self._get_method(
                    class_path=class_path,
                    method_name=method_name
                )

                method_params = self._get_method_params(method_map)

                # Executed the method if it's callable else assume it is a property or
                # attr and return the value
                if isinstance(method, Callable):
                    method_result = method(**method_params)
                else:
                    method_result = method

                # If a post hook is defined, get the method and execute it
                if class_map.get('post_hook') is not None:
                    post_hook_method = getattr(instance, class_map['post_hook'])
                    post_hook_method()

                self._logger.info(f'Command result for {class_path}.{method_name}: {method_result}')

                # Format the result if a formatter is defined as return value
                formatter = method_map.get('formatter')
                if formatter is not None and isinstance(method_result, dict):
                    return formatter.format(**method_result)
                return method_result
        else:
            logger_message = f'Unable to find method for {self.command}'
            self._logger.warning(logger_message)
            raise NotImplementedError(logger_message)












