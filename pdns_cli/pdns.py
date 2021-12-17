#!/usr/bin/env python3

from __future__ import print_function

import argparse
import requests.exceptions
import sys
import argcomplete
import toml
import os
import colored

from datetime import datetime
from operator import attrgetter
from .commands import *

from .api import PDNSAPI


class PDNSClient(object):

    @property
    def commands(self):
        """
        A dict of all command modules indexed with their name.
        """
        return {klass.name(): klass for klass in PDNSCommand.__subclasses__()}

    def run(self):
        """
        Main execution path.

        Load all command module klasses into the command map

        Parse the cli args using argparse (including command module subparsers)

        Load the config file if one can be found

        Merge the cli args and config file args

        Validate we have required arguments (from config or cli)

        Setup the API and execute the appropriate command module
        """

        self.load_modules()

        self.parse_cli_args()

        self.load_config_file()

        # This is None when no config file was found/available/specified etc
        if self.config_path:
            self.generate_zone_map()
            self.combine_cli_args_and_config()

        validate = self.validate_arguments()
        if validate != 0:
            sys.exit(validate)

        if self.args.auth:
            auth = tuple(self.args.auth.split(':', 1))
        else:
            auth = None

        self.api = PDNSAPI(self.args.url, verify=(not self.args.insecure),
                           basic_auth=auth, api_key=self.args.api_key)

        # Look up the action to see if it's implemented in a module, or raise an error
        cmd = self.args.action
        if cmd in self.cmd_map:
            moduleklass = self.cmd_map[cmd]
            # instance and pass in args and API instance
            module = moduleklass(self.args, self.api)
            # TODO better error handling
            try:
                module.run()
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 422 and 'error' in e.response.json():
                    self.error('API error: {}', e.response.json()['error'])
                    sys.exit(1)
                else:
                    self.error('HTTP error: {}', e)
                    sys.exit(1)
            except PDNSCommandException as e:
                self.error('{}: error: {}', cmd, str(e))
                sys.exit(1)

        else:
            sys.stderr.write('FIXME: {}: action not implemented\n'.format(self.args.action))
            sys.exit(1)

    def error(self, msg, *args, **kwargs):
        """
        Format and print error on stderr, print in red if in a tty.
        """
        if sys.stdout.isatty():
            sys.stderr.write(colored.stylize(msg.format(*args, **kwargs), colored.fg('red')) + '\n')
        else:
            sys.stderr.write(msg.format(*args, **kwargs) + '\n')

    def load_modules(self):
        """
        Create a map of the action subparser cmd to the class that implements
        that command
        """
        self.cmd_map = dict()
        for modulename, moduleklass in self.commands.items():
            for command in moduleklass.COMMANDS:
                self.cmd_map[command] = moduleklass

    def validate_arguments(self):
        """
        Ensure that required arguments are present, or die with a nice error message
        If this method returns a non zero value sys.exit is called with the return value
        """
        final = 0 # We start out with a working command

        if not self.args.url:
            self.error('The PowerDNS API URL is required')
            final = 2

        if not self.args.api_key and not self.args.auth:
            self.error('An API key or user:token combination is required')
            final = 2

        if self.args.action != 'list-servers' and not self.args.server:
            self.error('You must specify a server ID')
            final = 2

        return final

    def combine_cli_args_and_config(self):
        """
        Combine the cli args and configs provided by the config file (if any)
        CLI args always take priority over config in all instances
        """
        if 'api' in self.config:
            api = self.config['api']
        else:
            self.error('No api section in config file, please check the config file and try again')
            return

        if 'url' in api and not self.args.url:
            self.args.url = api['url']

        if 'default-server' in api and not self.args.server:
            self.args.server = api['default-server']

        if not self.args.auth and not self.args.api_key:
            self.args.auth = self.lookup_api_user(api)

    def lookup_api_user(self, api):
        """
        Based on the zone being edited and the default-user in the conf file select the appropriate api-user or key
        """
        auth = None
        if 'default-user' not in api:
            self.error('No default user specified in API section in configuration file')
            return
        if api['default-user'] not in self.config:
            self.error('Default user in configuration does not have associated entry, check your conf file syntax')
            return

        final_user_conf = self.config[api['default-user']]

        # If a zone is given and this zone has a mapped api user load that user from conf file
        if 'zone' in self.args and (self.args.zone in self.zone_map):
            final_user_conf = self.zone_map[self.args.zone]
            final_user_conf = self.config[final_user_conf]

        if final_user_conf and not self.args.auth and ('user' in final_user_conf and 'key' in final_user_conf):
            auth = '{}:{}'.format(final_user_conf['user'], final_user_conf['key'])
        return auth

    def load_config_file(self):
        """
        Load config file from either envvar or commandline option (higher priority)
        """
        self.config = None
        self.config_path = None
        if 'PDNS_CLI_CONF_PATH' in os.environ:
            self.config_path = os.environ['PDNS_CLI_CONF_PATH']

        if self.args.config_path:
            self.config_path = self.args.config_path

        if self.config_path:
            self.config = toml.load(self.config_path)

    def generate_zone_map(self):
        """
        Given the conf dict, search for keys that start with user and retreive their zones
        attribute, then iterate through it and create a new mapping of zone -> full user key
        we can then look this up later when deciding what user/key to use for the api call
        """
        self.zone_map = dict()
        for key, dictmap in self.config.items():
            if key.startswith('user'):
                if 'zones' in dictmap:
                    for zone in dictmap['zones']:
                        self.zone_map[zone] = key

    def parse_cli_args(self):
        """
        Command line argument processing and autocompletion.
        """

        # Top level parser arguments
        parser = argparse.ArgumentParser(description='CLI client for the PowerDNS API')
        parser.add_argument('-a', '--auth', metavar='USERNAME:PASSWORD', help='credentials for Basic authentication')
        parser.add_argument('-k', '--api-key', help='API key')
        parser.add_argument('-i', '--insecure', action='store_true', help='allow insecure TLS connections')
        parser.add_argument('-c', '--config-path', help='give a different config file path')
        parser.add_argument('-u', '--url', help='PowerDNS API URL')
        parser.add_argument('-s', '--server', help='server ID')


        subparsers = parser.add_subparsers(title='actions', metavar='action', dest='action')
        subparsers.required = True

        zone_parser = argparse.ArgumentParser(add_help=False)
        zone_parser.add_argument('zone', help='zone ID')

        for modulename, moduleklass in self.commands.items():
            moduleklass.init_parser(subparsers, zone_parser)

        argcomplete.autocomplete(parser)
        self.args = parser.parse_args()

    def fail(self, msg):
        sys.stderr.write('error: {}\n'.format(msg))
        sys.exit(1)

    def list_config(self, args):
        server = self.api.server(self.args.server)

        for setting in sorted(server.config, key=attrgetter('id')):
            print('{}: {}'.format(setting.data['name'], setting.data['value']))

def main():
    pdns_client = PDNSClient()
    pdns_client.run()
