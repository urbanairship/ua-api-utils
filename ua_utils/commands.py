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
    active = 0
    for apid_data in apid_json:
        if apid_data['active'] is True:
            active += 1
    return active


@cmd('get-apids')
def get_apids(options):
    """Get all apids for an app"""
    logger.info('Retrieving apids and saving to %s' % options.outfile)
    resp = requests.get('https://go.urbanairship.com/api/apids/',
                       params={'limit': 5},
                       auth=(options.app_key, options.secret))
    apids = {'apids': resp.json['apids'], 'active_apids': 0}
    apids['active_apids'] = tally_active_apids(resp.json['apids'])

    count = len(apids['apids'])
    logger.info('Retrieved %d apids' % count)

    while resp.json.get('next_page'):
        resp = requests.get(resp.json['next_page'],
                            auth=(options.app_key, options.secret))
        apids['apids'].extend(resp.json['apids'])
        count = len(apids['apids'])
        logger.info('Retrieved %d apids' % count)
        apids['active_apids'] += tally_active_apids(resp.json['apids'])
    logger.info('Done, saving to %s' % (options.outfile or '-'))
    if not options.outfile or options.outfile == '-':
        f = sys.stdout
    else:
        f = open(options.outfile, 'w')
    json.dump(apids, f, indent='    ')


def get_unique_users():
    pass


@cmd('get-user_ids')
def get_users(options):
    """Get all user_ids for an app"""
    logger.info('Retrieving user_ids and saving to %s' % options.outfile)
    # Check to see if users acccepts limit params
    # Format of request url
    #   'https://go.urbanairship.com/api/users/<start>/<count>'
    #       Seems to chunk in 10s no matter what
    #       Also appears to not be ordered in response depending on
    #       how many are requested at once
    index = 0
    increment = 10
    url = 'https://go.urbanairship.com/api/users/%d/%d' % (index, increment)
    resp = requests.get(url, auth=(options.app_key, options.secret))
    user_ids = []
    # Check to see if users from request are all dupes
    #   This should be separate as we can use this for the unique users count pulled down
    while [u_id for u_id in resp.json['users'] if u_id not in user_ids]:
        
    # Work around for user endpoint doing wonky things
    #   - Endpoint can return some dupes before end of list.
    #       - Check for entire list being a dupe?
    #           - Run some further testing on this
    # Check for dupes
    # If the payload is full of dupes end requests
    # If the payload has uniques add to user_ids and continue
    # Where to store/track the list of user_ids?
    # Can this be popped out for multiproc?
        # Pass the tuple return through the queue, unpack from get?
    # After work this weekend the API will return the ending user_ids
    #   repeatedly after the end of users is reached.
    #   - Need to find out if it only returns last 10 over and over?
    #   - Is this the behavior while the index is out of range?
    # Need to set a flag for a dupe user seen
    # Flow: (Each a separate call)
    #   - Get user ids
    #   - Check for dupes
    #   - Get unique user_ids
    #   - Get unqiue users
    #   - Repeat
    #unique_users, unique_user_ids = get_unique_users(resp.json['users'])
    #user_ids = {'user_ids': unique_users}
    #count = len(user_ids['user_ids'])

    logger.info('Retrieved %d apids' % count)
    while resp.json.get('next_page'):
        resp = requests.get(resp.json['next_page'],
                            auth=(options.app_key, options.secret))
        apids['apids'].extend(resp.json['apids'])
        count = len(apids['apids'])
        logger.info('Retrieved %d apids' % count)
        apids['active_apids'] += tally_active_apids(resp.json['apids'])
    logger.info('Done, saving to %s' % (options.outfile or '-'))
    if not options.outfile or options.outfile == '-':
        f = sys.stdout
    else:
        f = open(options.outfile, 'w')
    json.dump(apids, f, indent='    ')
