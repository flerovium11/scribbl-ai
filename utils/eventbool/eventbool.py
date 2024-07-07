from typing import Callable


class EventBool:
    def __init__(self: any, change_function: Callable, initial_state=True) -> None:
        self.state = initial_state
        self.change_function = change_function

    def switch_true(self: any) -> bool:
        """
        @returns True if the state has changed
        """
        if not self.state:
            self.change_function()
            self.state = True
            return True

    def switch_false(self: any) -> bool:
        """
        @returns True if the state has changed
        """
        if self.state:
            self.change_function()
            self.state = False
            return True
