from . import PDNSCommand
class CRYPTOKEY(PDNSCommand):
    NAME = 'cryptokey'
    DESCRIPTION = 'cryptokey related API actions'
    COMMANDS = ['list-cryptokeys', 'show-cryptokey', 'edit-cryptokey', 'add-cryptokey', 'delete-cryptokey']

    @classmethod
    def init_parser(cls, subparsers, zone_parser):
        # cryptokeys

        subparsers.add_parser('list-cryptokeys', help='list all cryptokeys from a zone')

        subparsers.add_parser('show-cryptokey', help='show a cryptokey from a zone')

        subparsers.add_parser('add-cryptokey', help='add a new cryptokey to a zone')

        subparsers.add_parser('edit-cryptokey', help='edit a cryptokey from a zone')

        subparsers.add_parser('delete-cryptokey', help='delete a cryptokey from a zone')

    def run(self):
        getattr(self, (self.args.action).replace('-', '_'))()
