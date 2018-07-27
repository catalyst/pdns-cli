import colored
import sys


__all__ = (
    'PDNSCommand', 'PDNSCommandException',
    'server',
    'zone',
    'rrset',
    'metadata',
    'cryptokey',
    'cache',
    'config',
    'search',
    'statistics',
)


class PDNSCommandException(Exception):
    pass


class PDNSCommand(object):

    NAME = '__setme__'
    DESCRIPTION = '__setme__'
    COMMANDS = []

    @classmethod
    def name(cls):
        """
        Return command name.
        """
        return cls.NAME

    @classmethod
    def description(cls):
        """
        Return command description.
        """
        return cls.DESCRIPTION


    @classmethod
    def init_parser(cls, parser, edb, site=None):
        """
        Override to add command line arguments to the command.
        """
        pass

    @classmethod
    def validate_arguments(cls, args):
        """
        Override to add custom argument checks that argparse cannot do.
        """
        if cls.REQUIRES_SERVER and 'server' not in args:
            return (2, 'You did not specify a server')

    def __init__(self, args, api):
        """
        Initialize command: store args
        """
        self.args = args
        self.api = api

    def run(self):
        """
        Override to make the command do something.
        """
        pass

    def pretty_print(self, msg, *args, **kwargs):
        """
        Format and print messages on stdout, print arguments in bold if in a tty.
        """
        if sys.stdout.isatty():
            pretty_args = [colored.stylize(arg, colored.attr('bold')) for arg in args]
            pretty_kwargs = {key: colored.stylize(arg, colored.attr('bold')) for key, arg in kwargs.items()}
            print(msg.format(*pretty_args, **pretty_kwargs))
        else:
            print(msg.format(*args, **kwargs))

    def fail(self, msg, *args, **kwargs):
        """
        Throw an exception to be caught by the main method to abort the command.
        """
        raise PDNSCommandException(msg.format(*args, **kwargs))
