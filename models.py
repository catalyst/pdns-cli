import json
class Model(object):

    name = None
    id_attr = 'id'

    def __init__(self, api, id, parent=None, data={}):
        self.api = api
        self.id = id
        self.parent = parent
        self._data = data

    @classmethod
    def all(cls, api, parent=None):
        return [cls(api, item[cls.id_attr], parent=parent, data=item)
                for item in api.get(cls.collection_path(parent)).json()]

    @classmethod
    def collection_path(cls, parent=None):
        if parent is not None:
            return '/'.join((parent.path, cls.name))
        return cls.name

    @property
    def path(self):
        if self.parent is not None:
            return '/'.join((self.parent.path, self.name, self.id))
        return '/'.join((self.name, self.id))

    @property
    def data(self):
        if not self._data:
            self.load()
        return self._data

    @classmethod
    def create(cls, api, parent=None, data={}):
        response = api.post(cls.collection_path(parent), json=data)
        response_json = ''
        # If the response was 204 no content success, the update worked
        # Fill out the response json with the inbound data
        if response.status_code == 204:
            response_json = json.dumps(data)
        else:
            response_json = response.json()
        return cls(api, response_json[cls.id_attr], parent=parent, data=response_json)

    def load(self):
        response = self.api.get(self.path)
        self._data = response.json()

    reload = load

    def update(self, **kwargs):
        # If the response was 204 no content success, the update worked
        # Fill out the response json with the inbound data
        response = self.api.put(self.path, json=kwargs)
        if response.status_code == 204:
            response_json = json.dumps(kwargs)
        else:
            response_json = response.json()
        self._data = response_json

    def delete(self):
        self.api.delete(self.path)
        self._data = {}

    def __repr__(self):
        return '<{} {}>'.format(type(self).__name__, self.id)


class Server(Model):

    name = 'servers'

    @property
    def config(self):
        return ConfigSetting.all(self.api, parent=self)

    def config_setting(self, name):
        return ConfigSetting(self.api, name, parent=self)

    @property
    def zones(self):
        return Zone.all(self.api, parent=self)

    def zone(self, name):
        return Zone(self.api, name, parent=self)

    def create_zone(self, name, kind='Master', nameservers=[], **kwargs):
        data = kwargs
        data.update({'name': name, 'kind': kind, 'nameservers': nameservers})
        return Zone.create(self.api, parent=self, data=data)

    def delete_zone(self, name):
        return Zone(self.api, name, parent=self).delete()


class ConfigSetting(Model):

    name = 'config'
    id_attr = 'name'


class Zone(Model):

    name = 'zones'

    @property
    def rrsets(self):
        return {RRset(**rrset) for rrset in self.data['rrsets']}

    def update_rrsets(self, rrsets, delete=False):
        rrsets_changes = []
        for rrset in rrsets:
            rrset_change = rrset.to_dict()
            if delete:
                rrset_change['changetype'] = 'DELETE'
                rrset_change['records'] = []
                rrset_change['comments'] = []
                del rrset_change['ttl']
            else:
                rrset_change['changetype'] = 'REPLACE'
            rrsets_changes.append(rrset_change)
        self.api.patch(self.path, json={'rrsets': rrsets_changes})
        self._data = {}  # clear to force refresh on next access

    #Send a DNS NOTIFY to all slaves.
    def notify(self):
        self.api.put('{0}/notify'.format(self.path))

class RRset(object):

    def __init__(self, name, type, content=None, disabled=False, ttl=None, records=[], comments=[]):
        self.name = name
        self.type = type
        self.content = content
        self.disabled = disabled
        self.ttl = ttl
        self.records = {Record(**record) for record in records}
        self.comments = {Comment(**comment) for comment in comments}

    def to_dict(self):
        return {
            'name': self.name,
            'type': self.type,
            'ttl': self.ttl,
            'content': self.content,
            'disabled': self.disabled,
            'records': [record.to_dict() for record in self.records],
            'comments': [comment.to_dict() for comment in self.comments]
        }

    def __eq__(self, other):
        return self.name == other.name and self.type == other.type

    def __hash__(self):
        return hash((self.name, self.type))


class Record(object):

    def __init__(self, content, disabled=False, set_ptr=False):
        self.content = content
        self.disabled = disabled
        self.set_ptr = set_ptr

    def to_dict(self):
        return {
            'content': self.content,
            'disabled': self.disabled,
            'set_ptr': self.set_ptr
        }

    def __eq__(self, other):
        return self.content == other.content

    def __hash__(self):
        return hash((self.content,))


class Comment(object):

    def __init__(self, content, account, modified_at):
        self.content = content
        self.account = account
        self.modified_at = modified_at

    def to_dict(self):
        return {
            'content': self.content,
            'account': self.account,
            'modified_at': self.modified_at
        }

    def __eq__(self, other):
        return self.content == other.content

    def __hash__(self):
        return hash((self.content,))


class Metadata(Model):

    name = 'metadata'
    id_attr = 'kind'


class Cryptokey(Model):

    name = 'cryptokeys'
