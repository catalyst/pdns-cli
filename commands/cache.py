from . import PDNSCommand
class CACHE(PDNSCommand):
    NAME = 'cache'
    DESCRIPTION = 'cache related API actions'
    COMMANDS = ['cache']

    @classmethod
    def init_parser(cls, subparsers, zone_parser):
        subparsers.add_parser('flush-cache', help='flush the cache for a given domain name')

    def run(self):
        getattr(self, (self.args.action).replace('-', '_'))()
