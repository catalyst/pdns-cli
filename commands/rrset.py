from . import PDNSCommand
from operator import attrgetter
from models import RRset,Record,Comment
class RRSET(PDNSCommand):
    NAME = 'rrset'
    DESCRIPTION = 'RRset related API actions'
    COMMANDS = ['show-rrsets', 'edit-rrset', 'delete-rrset', 'edit-rrset-comments']

    @classmethod
    def init_parser(cls, subparsers, zone_parser):

        subparsers.add_parser('show-rrsets', parents=[zone_parser], help='show Resource Record sets for a zone')

        edit_rrset = subparsers.add_parser('edit-rrset', parents=[zone_parser],
                                           help='add/replace/delete a record in Resource Record set')
        edit_rrset_mode = edit_rrset.add_mutually_exclusive_group(required=True)
        edit_rrset_mode.add_argument('--add', action='store_const', dest='mode', const='add',
                                     help='add a record for a domain/subdomain')
        edit_rrset_mode.add_argument('--replace', action='store_const', dest='mode', const='replace',
                                     help='replace all records for a domain/subdomain')
        edit_rrset_mode.add_argument('--delete', action='store_const', dest='mode', const='delete',
                                     help='delete a record for a domain/subdomain')
        edit_rrset.add_argument('--disabled', action='store_true', help='disable record')
        edit_rrset.add_argument('--set-ptr', action='store_true', help='set PTR records in matching reverse zones')
        edit_rrset.add_argument('--ttl', type=int, default=3600, help='record TTL')
        edit_rrset.add_argument('name', help='record name')
        edit_rrset.add_argument('type', help='record type')
        edit_rrset.add_argument('content', help='record content')

        delete_rrset = subparsers.add_parser('delete-rrset', parents=[zone_parser],
                                             help='delete a Resource Record set')
        delete_rrset.add_argument('name', help='record name')
        delete_rrset.add_argument('type', help='record type')

        edit_rrset_comments = subparsers.add_parser('edit-rrset-comments', parents=[zone_parser],
                                                    help='add/replace/delete a comment in Resource Record set')
        edit_rrset_comments_mode = edit_rrset_comments.add_mutually_exclusive_group(required=True)
        edit_rrset_comments_mode.add_argument('--add', action='store_const', dest='mode', const='add',
                                              help='add a comment for a domain/subdomain')
        edit_rrset_comments_mode.add_argument('--replace', action='store_const', dest='mode', const='replace',
                                              help='replace all comments for a domain/subdomain')
        edit_rrset_comments_mode.add_argument('--delete', action='store_const', dest='mode', const='delete',
                                              help='delete a comment for a domain/subdomain')
        edit_rrset_comments.add_argument('--account', default='', help='comment account')
        edit_rrset_comments.add_argument('name', help='record name')
        edit_rrset_comments.add_argument('type', help='record type')
        edit_rrset_comments.add_argument('content', help='record content')


    def run(self):
        getattr(self, (self.args.action).replace('-', '_'))()

    def show_rrsets(self):
        server = self.api.server(self.args.server)
        zone = server.zone(self.args.zone)

        # base domain first
        for rrset in sorted([rrset for rrset in zone.rrsets if rrset.name == zone.data['name']],
                            key=attrgetter('name', 'type')):
            self._print_rrset(rrset)

        # subdomains next
        for rrset in sorted([rrset for rrset in zone.rrsets if rrset.name != zone.data['name']],
                            key=attrgetter('name', 'type')):
            self._print_rrset(rrset)

    def _print_rrset(self, rrset):
        for comment in sorted(rrset.comments, key=attrgetter('modified_at')):
            if comment.account:
                print(';; {} by {}: {}'.format(datetime.fromtimestamp(comment.modified_at).isoformat(),
                                               comment.account, comment.content))
            else:
                print(';; {}: {}'.format(datetime.fromtimestamp(comment.modified_at).isoformat(),
                                         comment.content))

        for record in sorted(rrset.records, key=attrgetter('content')):
            line = "{}\t{}\tIN\t{}\t{}".format(rrset.name, rrset.ttl, rrset.type, record.content)
            if record.disabled:
                line = "; {} ; DISABLED".format(line)
            print(line)

    def edit_rrset(self):
        server = self.api.server(self.args.server)
        zone = server.zone(self.args.zone)

        name = self.args.name
        if not name.endswith('.'):
            name = '{}.{}'.format(name, zone.data['name'])

        new_rrset = RRset(name=name, type=self.args.type)
        # look for existing rrset
        for rrset in zone.rrsets:
            if rrset == new_rrset:
                new_rrset = rrset
                break

        new_rrset.ttl = self.args.ttl

        record = Record(content=self.args.content, disabled=self.args.disabled, set_ptr=self.args.set_ptr)
        if self.args.mode == 'add':
            new_rrset.records.add(record)
        elif self.args.mode == 'replace':
            new_rrset.records.clear()
            new_rrset.records.add(record)
        elif self.args.mode == 'delete':
            new_rrset.records.discard(record)

        zone.update_rrsets([new_rrset])

    def delete_rrset(self):
        server = self.api.server(self.args.server)
        zone = server.zone(self.args.zone)

        name = self.args.name
        if not name.endswith('.'):
            name = '{}.{}'.format(name, zone.data['name'])

        rrset = RRset(name=name, type=self.args.type)
        zone.update_rrsets([rrset], delete=True)

    def edit_rrset_comments(self):
        server = self.api.server(self.args.server)
        zone = server.zone(self.args.zone)

        name = self.args.name
        if not name.endswith('.'):
            name = '{}.{}'.format(name, zone.data['name'])

        new_rrset = RRset(name=name, type=self.args.type)
        # look for existing rrset
        for rrset in zone.rrsets:
            if rrset == new_rrset:
                new_rrset = rrset
                break

        if not new_rrset.records:  # no records means it didn't come from the API
            self.fail('RRset {}/{} not found'.format(name, self.args.type))

        comment = Comment(content=self.args.content, account=self.args.account, modified_at=time.time())
        if self.args.mode == 'add':
            new_rrset.comments.add(comment)
        elif self.args.mode == 'replace':
            new_rrset.comments.clear()
            new_rrset.comments.add(comment)
        elif self.args.mode == 'delete':
            new_rrset.comments.discard(comment)

        zone.update_rrsets([new_rrset])

