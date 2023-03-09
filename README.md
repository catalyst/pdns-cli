# PowerDNS HTTPS API client

This a PowerDNS HTTPS API client implementation in Python. For more information about the PowerDNS API see [the PowerDNS documentation](https://doc.powerdns.com/authoritative/http-api/).

## Getting started

### Prerequisites

[python-requests](http://docs.python-requests.org/)

[toml](https://pypi.org/project/toml/0.9.2/)

[colored](https://pypi.org/project/colored/)

[argcomplete](http://argcomplete.readthedocs.io/en/latest/index.html)

### Installing

Create a virtual environment and install the necessary packages:

```
pip install -r requirements.txt
```

## Example usage

Adding a `www` hostname to the `localhost` server for the `example.org` domain, with an A record of `192.0.5.9`

The zone name must always end with a `.` character so it is "full qualified".

```
# with config file
./pdns -c conf.toml edit-rrset --add example.org. www A 192.0.5.9
# without
./pdns -a user:token -u https://dns.example.com/api/v1/ -s localhost edit-rrset --add example.org. www A 192.0.5.9
```

Editing the `www` hostname to have a different IP for the `A` record:

```
./pdns -c conf.toml edit-rrset --replace example.org. www A 192.0.5.10
./pdns -a user:token -u https://dns.example.com/api/v1/ -s localhost edit-rrset --replace example.org. www A 192.0.5.10
```

List RRsets in the `example.org` zone:

```
./pdns -c conf.toml show-rrsets localhost example.org.
./pdns -a user:token -u https://dns.example.com/api/v1/ -s localhost show-rrsets localhost example.org.
```

Changing an RRsets type requires deleting the old RRset and adding it as the new type as two operations

## Configuration

While you can specify at runtime all details required to connect to a PowerDNS API, it's much more ergonomic to instead use a configuration file. This is a file in the [.toml](https://github.com/toml-lang/toml) format located in one of the following two places

- the path specified in the `PDNS_CLI_CONF_PATH` os environment variable
- the path provided by the optional cli argument `-c or --config-path`

The format is documented in the [conf.toml.dist](https://gitlab.catalyst.net.nz/elearning/pdns-cli/blob/master/conf.toml.dist) file included in the repository and allows you to specify standard details for your environment

Things you can specify include
- PowerDNS API URL
- The server id to operate on
- You can specify multiple users and a list of zones each user is for, pdns-cli will select the appropriate user based on the zone being edited

Using the `-c` command has precedence over the environment variable, so you can have a default configuration file and then override on an as needed basis

Using a configuration file is highly recommended - compare:

```
./pdns edit-rrset --add example.org. www A 192.0.5.9
./pdns edit-rrset --add notexample.org. www CNAME example.org.
```

and

```
./pdns -k superawesomekey -u https://yourdnsapi.com/api/v1/ -s localhost edit-rrset --add example.org. www A 192.0.5.9
./pdns -k superawesomekey2 -u https://yourdnsapi.com/api/v1/ -s localhost edit-rrset --add notexample.org. www CNAME example.org.
```

## Full command list 
**A ! at the command start indicates unimplemented API calls**
```
usage: pdns [-h] [-a USERNAME:PASSWORD] [-k API_KEY] [-i] [-c CONFIG_PATH]
            [-u URL] [-s SERVER]
            action ...

CLI client for the PowerDNS API

optional arguments:
  -h, --help            show this help message and exit
  -a USERNAME:PASSWORD, --auth USERNAME:PASSWORD
                        credentials for Basic authentication
  -k API_KEY, --api-key API_KEY
                        API key
  -i, --insecure        allow insecure TLS connections
  -c CONFIG_PATH, --config-path CONFIG_PATH
                        give a different config file path
  -u URL, --url URL     PowerDNS API URL
  -s SERVER, --server SERVER
                        server ID

actions:
  action
    list-servers        list servers
    show-server         show details for a server
    !add-server          add a new server (pdnscontrol only)
    !edit-server         add a new server (pdnscontrol only)
    delete-server       delete a server (pdnscontrol only)
    list-config         list config settings
    list-zones          list zones
    show-zone           show details for a zone
    add-zone            add a new zone, return zone ID
    edit-zone           add a new zone
    delete-zone         delete a zone
    show-rrsets         show Resource Record sets for a zone
    edit-rrset          add/replace/delete a record in Resource Record set
    delete-rrset        delete a Resource Record set
    edit-rrset-comments add/replace/delete a comment in Resource Record set
    notify              send a DNS NOTIFY to all slaves for a zone
    !axfr-retrieve       retrieve a zone from the master
    !export              export a zone in AXFR format
    !check               verify a zone content/configuration
    !list-metadata       list all metadata for a zone
    !show-metadata       show metadata of a given kind for a zone
    !add-metadata        add a new set of metadata for a zone
    !edit-metadata       edit a set of metadata for a zone
    !delete-metadata     delete all metadata of a given kind for a zone
    !list-cryptokeys     list all cryptokeys from a zone
    !show-cryptokey      show a cryptokey from a zone
    !add-cryptokey       add a new cryptokey to a zone
    !edit-cryptokey      edit a cryptokey from a zone
    !delete-cryptokey    delete a cryptokey from a zone
    !search              search across all zones, records and comments
    !search-log          search in the log
    !statistics          show internal statistics
    !flush-cache         flush the cache for a given domain name
```
## TODO

See [TODO](TODO.md).

## Authors

* **Pierre Guinoiseau** - *Initial work*
* **Francis Devine** - *Configuration files*
