from typing import List

import AgentCore.engine
from AgentCore.context import Context
from Command.command_base import CommandBase

class Command(CommandBase):

    @classmethod
    def run(cls, args: List[str]):
        if len(args) < 1:
            args[0] = input("Project name: ").strip()
            args[1] = input("Project root path: ").strip()
        AgentCore.engine.CONTEXT = Context.create_context(args[0], args[1])

    @classmethod
    def help(cls):
        print("""Create - Command used in order to create a new project.
        Usage:
        create <project_name> <project_root_path>
        
        All created projects are stored inside of the user's home folder.""")