from . import PDNSCommand
class SEARCH(PDNSCommand):
    NAME = 'search'
    DESCRIPTION = 'search related API actions'
    COMMANDS = ['search', 'search-log']

    @classmethod
    def init_parser(cls, subparsers, zone_parser):
        # search

        subparsers.add_parser('search', help='search across all zones, records and comments')

        subparsers.add_parser('search-log', help='search in the log')

    def run(self):
        self.fail('This command is not yet implemented')
