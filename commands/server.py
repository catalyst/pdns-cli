from . import PDNSCommand
from operator import attrgetter
class SERVER(PDNSCommand):
    NAME = 'server'
    DESCRIPTION = 'Server related API actions'
    COMMANDS = ['list-servers', 'show-server', 'add-server', 'edit-server', 'delete-server']

    @classmethod
    def init_parser(cls, subparsers, zone_parser):
        # servers
        subparsers.add_parser('list-servers', help='list servers')

        subparsers.add_parser('show-server', help='show details for a server')

        subparsers.add_parser('add-server', help='add a new server (pdnscontrol only)')

        subparsers.add_parser('edit-server', help='add a new server (pdnscontrol only)')

        subparsers.add_parser('delete-server', help='delete a server (pdnscontrol only)')

    def run(self):
        getattr(self, (self.args.action).replace('-', '_'))()

    def list_servers(self):
        for server in sorted(self.api.servers, key=attrgetter('id')):
            print(server.id)

    def show_server(self):
        server = self.api.server(self.args.server)

        for key, value in sorted(server.data.items()):
            if key == 'url' or key.endswith('_url'):
                continue
            print('{}: {}'.format(key, value))

    def edit_server(self):
        pass  # FIXME: implement me

    def delete_server(self):
        server = self.api.server(self.args.server)

        server.delete()


