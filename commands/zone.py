from . import PDNSCommand
from operator import attrgetter
class ZONE(PDNSCommand):
    NAME = 'zone'
    DESCRIPTION = 'Zone related API actions'
    COMMANDS = ['list-zones', 'show-zone', 'add-zone', 'edit-zone']

    def __init__(self, *args, **kwargs):
        """
        Initialize command: store args
        """
        super(ZONE, self).__init__(*args, **kwargs)
        self.editable_zone_values = ['masters', 'servers', 'account', 'recursion_desired', 'soa_edit', 'soa_edit_api']

    @classmethod
    def init_parser(cls, subparsers, zone_parser):
        # zones
        subparsers.add_parser('list-zones', help='list zones')

        subparsers.add_parser('show-zone', parents=[zone_parser], help='show details for a zone')

        add_zone = subparsers.add_parser('add-zone',
                                         help='add a new zone, return zone ID')
        add_zone.add_argument('name', help='zone name (must include the trailing dot)')
        add_zone.add_argument('--kind', choices=('Native', 'Master', 'Slave', 'Forwarded'), default='Master',
                              help='kind of zone')
        add_zone.add_argument('--nameservers', nargs='+', default=[], metavar="NAMESERVER",
                              help='nameserver names (must include the trailing dot) (authoritative only)')
        add_zone.add_argument('--masters', nargs='+', metavar="SERVER", help='master servers')
        add_zone.add_argument('--servers', nargs='+', metavar="SERVER",
                              help='forwarded-to servers (recursor only)')
        add_zone.add_argument('--account', help='account (authoritative only)')
        add_zone.add_argument('--recursion-desired', action='store_true',
                              help='set the RD bit for forwarded zones (authoritative only)')
        add_zone.add_argument('--soa-edit-api', choices=('DEFAULT', 'INCREASE', 'EPOCH', 'SOA-EDIT', 'SOA-EDIT-INCREASE'), help='SOA EDIT API setting')
        add_zone.add_argument('--soa-edit', choices=('INCREMENT-WEEKS', 'INCEPTION-EPOCH', 'INCEPTION-INCREMENT', 'EPOCH', 'NONE'), help='SOA EDIT setting for dnssec https://doc.powerdns.com/authoritative/dnssec/operational.html#soa-edit-ensure-signature-freshness-on-slaves')

        edit_zone = subparsers.add_parser('edit-zone', parents=[zone_parser], help='add a new zone')
        edit_zone.add_argument('--kind', choices=('Native', 'Master', 'Slave', 'Forwarded'), help='kind of zone')
        edit_zone.add_argument('--masters', nargs='+', metavar="SERVER", help='master servers')
        edit_zone.add_argument('--servers', nargs='+', metavar="SERVER",
                               help='forwarded-to servers (recursor only)')
        edit_zone.add_argument('--account', help='account (authoritative only)')
        edit_zone.add_argument('--recursion-desired', action='store_true',
                               help='set the RD bit for forwarded zones (authoritative only)')
        edit_zone.add_argument('--soa-edit-api', choices=('DEFAULT', 'INCREASE', 'EPOCH', 'SOA-EDIT', 'SOA-EDIT-INCREASE'), help='SOA EDIT API serial update strategy https://doc.powerdns.com/authoritative/domainmetadata.html#soa-edit-api')
        edit_zone.add_argument('--soa-edit', choices=('INCREMENT-WEEKS', 'INCEPTION-EPOCH', 'INCEPTION-INCREMENT', 'EPOCH', 'NONE'), help='SOA EDIT setting for dnssec https://doc.powerdns.com/authoritative/dnssec/operational.html#soa-edit-ensure-signature-freshness-on-slaves')

        subparsers.add_parser('delete-zone', parents=[zone_parser], help='delete a zone')

    def run(self):
        getattr(self, (self.args.action).replace('-', '_'))()

    def list_zones(self):
        server = self.api.server(self.args.server)

        for zone in sorted(server.zones, key=attrgetter('id')):
            print(zone.data['id'])

    def show_zone(self):
        server = self.api.server(self.args.server)
        zone = server.zone(self.args.zone)

        for key, value in sorted(zone.data.items()):
            if key in ['rrsets', 'url'] or key.endswith('_url'):
                continue
            print('{}: {}'.format(key, value))

    def add_zone(self):
        server = self.api.server(self.args.server)

        if not self.args.name.endswith('.'):
            self.fail('zone name must end with a dot!')

        if self.args.nameservers and any([ns for ns in self.args.nameservers if not ns.endswith('.')]):
            self.fail('nameservers name must end with a dot!')

        data = {key: getattr(self.args, key)
                for key in self.editable_zone_values
                if getattr(self.args, key) is not None}
        zone = server.create_zone(self.args.name, kind=self.args.kind, nameservers=self.args.nameservers, **data)

        print("Zone added with ID '{}'".format(zone.data['id']))

    def edit_zone(self):
        server = self.api.server(self.args.server)
        zone = server.zone(self.args.zone)

        data = {key: getattr(self.args, key)
                for key in self.editable_zone_values
                if getattr(self.args, key) is not None}
        # mandatory for some reason
        if 'kind' not in data:
            data['kind'] = zone.data['kind']
        zone.update(**data)

    def delete_zone(self):
        server = self.api.server(self.args.server)
        zone = server.zone(self.args.zone)

        zone.delete()
