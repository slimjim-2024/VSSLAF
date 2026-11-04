from Command.command_base import CommandBase


class Command(CommandBase):
    @classmethod
    def run(cls, args: list[str]):
        exit(0)