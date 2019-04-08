from . import PDNSCommand
class CONFIG(PDNSCommand):
    NAME = 'config'
    DESCRIPTION = 'config related API actions'
    COMMANDS = ['list-config', 'notify', 'axfr-retrieve', 'export', 'check']

    @classmethod
    def init_parser(cls, subparsers, zone_parser):
        # configs
        subparsers.add_parser('list-config', help='list config settings')

        subparsers.add_parser('notify', parents=[zone_parser], help='send a DNS NOTIFY to all slaves for a zone')

        subparsers.add_parser('axfr-retrieve', parents=[zone_parser], help='retrieve a zone from the master')

        subparsers.add_parser('export', parents=[zone_parser], help='export a zone in AXFR format')

        subparsers.add_parser('check', parents=[zone_parser], help='verify a zone content/configuration')

    def run(self):
        if self.args.action == 'notify':
            getattr(self, (self.args.action).replace('-', '_'))()
        else:
            self.fail('This command is not yet implemented')

    def notify(self):
        server = self.api.server(self.args.server)
        zone = server.zone(self.args.zone)
        zone.notify()
