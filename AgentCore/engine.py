from importlib import import_module

from AgentCore import context
from AgentCore.context import Context, ChatMessage
from AgentCore.custom_errors import InvalidArgumentType

CONTEXT: Context | None = None
SPECIAL_CHARACTER = "#"
SHOULD_EXIT = False

async def start_engine():
    global CONTEXT
    while not SHOULD_EXIT:
        if CONTEXT is None:
            print("Please use the #create command to create a new project")
        user_input = input("> ")
        if user_input.startswith(SPECIAL_CHARACTER):
            user_input = user_input[1:]
            user_input = user_input.split(" ")
            try:
                module = import_module(f"Command.{user_input[0]}")
                module_instance = module.Command()

                if (user_input.count() > 1 and user_input[1] in ["-h", "--help"]):
                    module_instance.help()

                else:
                    module_instance.run(user_input[1:])

            except ModuleNotFoundError:
                print(f"Module {user_input[0]} not found")
            except InvalidArgumentType:
                print(f"Invalid argument for function: {user_input[0]}")

        else:
            if CONTEXT is None:
                print("Please use the #create command to create a new project")
                continue
            CONTEXT.message_history.append(ChatMessage.model_validate({"role":"user", "content":user_input}))







