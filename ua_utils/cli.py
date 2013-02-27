import argparse
import logging
import os
import sys

from . import commands


logging.basicConfig(format='%(message)s')
logger = logging.getLogger('ua_utils.cli')
logger.setLevel(logging.INFO)

main_parser = argparse.ArgumentParser()
main_parser.add_argument('-v --verbose', dest='verbose', action='store_true',
        help='enable verbose logging')
main_parser.add_argument(
    'command', help='command to run [%s]' % ', '.join(commands.funcs)
)
main_parser.add_argument('app_key', help='app key for command')
main_parser.add_argument('secret', default=os.getenv('UA_SECRET'),
        help='API secret to use defaults to UA_SECRET')
main_parser.add_argument('-o --out', default='ua.json', dest='outfile',
        help='output file')


def main():
    """Command line interface's entry point"""
    options = main_parser.parse_args()
    handler = commands.get_command(options.command)
    if handler:
        handler(options)
    else:
        print 'Unknown command'
        print
        options.print_help()
        sys.exit(1)
