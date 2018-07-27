from . import PDNSCommand
class METADATA(PDNSCommand):
    NAME = 'metadata'
    DESCRIPTION = 'metadata related API actions'
    COMMANDS = ['list-metadata', 'show-metadata', 'edit-metadata', 'add-metadata', 'delete-metadata']

    @classmethod
    def init_parser(cls, subparsers, zone_parser):
        # metadata
        subparsers.add_parser('list-metadata', help='list all metadata for a zone')

        subparsers.add_parser('show-metadata', help='show metadata of a given kind for a zone')

        subparsers.add_parser('add-metadata', help='add a new set of metadata for a zone')

        subparsers.add_parser('edit-metadata', help='edit a set of metadata for a zone')

        subparsers.add_parser('delete-metadata', help='delete all metadata of a given kind for a zone')

    def run(self):
        getattr(self, (self.args.action).replace('-', '_'))()
