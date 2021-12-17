from . import PDNSCommand
class CACHE(PDNSCommand):
    NAME = 'cache'
    DESCRIPTION = 'cache related API actions'
    COMMANDS = ['flush-cache']

    @classmethod
    def init_parser(cls, subparsers, zone_parser):
        subparsers.add_parser('flush-cache', help='flush the cache for a given domain name')

    def run(self):
        self.fail('This command is not yet implemented')
