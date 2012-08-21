import logging
import sys

import simplejson as json
import requests

logger = logging.getLogger('ua_utils.cli')
_commands = {}


def cmd(name=None):
    def wrap(f):
        if name is None:
            cmd_name = f.__name__
        else:
            cmd_name = name
        _commands[cmd_name] = f
        return f
    return wrap


def get_command(name):
    """Returns a command handler function or None if command isn't found"""
    return _commands.get(name)


@cmd('get-tokens')
def get_tokens(options):
    """Get all device tokens for an app"""
    logger.info('Retrieving device tokens and saving to %s' % options.outfile)
    resp = requests.get('https://go.urbanairship.com/api/device_tokens/',
                        params={'limit': 5},
                        auth=(options.app_key, options.secret))
    tokens = {
        'device_tokens_count': resp.json['device_tokens_count'],
        'active_device_tokens_count':
            resp.json['active_device_tokens_count'],
        'device_tokens': resp.json['device_tokens']
    }

    count = len(tokens['device_tokens'])
    total = tokens['device_tokens_count']

    while resp.json.get('next_page'):
        logger.info('Retrieved %d of %d' % (count, total))
        resp = requests.get(resp.json['next_page'],
                            auth=(options.app_key, options.secret))
        count = len(tokens['device_tokens'])
        tokens['device_tokens'].extend(resp.json['device_tokens'])

    logger.info('Done, saving to %s' % (options.outfile or '-'))
    if not options.outfile or options.outfile == '-':
        f = sys.stdout
    else:
        f = open(options.outfile, 'w')
    json.dump(tokens, f, indent='    ')


def tally_active_apids(apid_json):
    """Get tally for active apids"""
    active = len([apid for apid in apid_json if apid['active']])
    return active


@cmd('get-apids')
def get_apids(options):
    """Get all apids for an app"""
    logger.info('Retrieving apids and saving to %s' % options.outfile)
    resp = requests.get('https://go.urbanairship.com/api/apids/',
                       params={'limit': 5},
                       auth=(options.app_key, options.secret))
    apids = resp.json['apids']
    active_apids = tally_active_apids(resp.json['apids'])
    count = len(apids)
    logger.info('Retrieved %d apids' % count)

    while resp.json.get('next_page'):
        resp = requests.get(resp.json['next_page'],
                            auth=(options.app_key, options.secret))
        apids.extend(resp.json['apids'])
        count = len(apids)
        logger.info('Retrieved %d apids' % count)
        active_apids += tally_active_apids(resp.json['apids'])
    apid_data = {'apids': apids, 'active_apids': active_apids}
    logger.info('Done, saving to %s' % (options.outfile or '-'))
    if not options.outfile or options.outfile == '-':
        f = sys.stdout
    else:
        f = open(options.outfile, 'w')
    json.dump(apid_data, f, indent='    ')
