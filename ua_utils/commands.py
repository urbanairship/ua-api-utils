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


def jsoncmd(fn):
    def wrap(*args, **kwargs):
        opt = args[0]
        if not opt.outfile or opt.outfile == '-':
            f = sys.stdout
        else:
            f = open(opt.outfile, 'w')
        json.dump(fn(*args, **kwargs), f, indent='    ')
        logger.info('Done, saving to %s' % (opt.outfile or '-'))
    return wrap


def get_command(name):
    """Returns a command handler function or None if command isn't found"""
    return _commands.get(name)


def api_req(endpoint, auth, params=None):
    """Make API request to UA API"""
    url = 'https://go.urbanairship.com/api/%s' % endpoint
    if params:
        r = requests.get(url, params=params, auth=auth)
    else:
        r = requests.get(url, auth=auth)
    return r


@cmd('get-tokens')
@jsoncmd
def get_tokens(options):
    """Get all device tokens for an app"""
    logger.info('Retrieving device tokens and saving to %s' % options.outfile)
    auth = (options.app_key, options.secret)
    resp = api_req('device_tokens/', auth, params={'limit': 5})
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
                            auth=auth)
        count = len(tokens['device_tokens'])
        tokens['device_tokens'].extend(resp.json['device_tokens'])

    return tokens


def tally_active_apids(apid_json):
    """Get tally for active apids"""
    active = len([apid for apid in apid_json if apid['active']])
    return active


@cmd('get-apids')
@jsoncmd
def get_apids(options):
    """Get all apids for an app"""
    logger.info('Retrieving apids and saving to %s' % options.outfile)
    auth = (options.app_key, options.secret)
    resp = api_req('apids/', auth, params={'limit': 5})
    apids = resp.json['apids']
    active_apids = tally_active_apids(resp.json['apids'])
    count = len(apids)
    logger.info('Retrieved %d apids' % count)

    while resp.json.get('next_page'):
        resp = requests.get(resp.json['next_page'],
                            auth=auth)
        apids.extend(resp.json['apids'])
        count = len(apids)
        logger.info('Retrieved %d apids' % count)
        active_apids += tally_active_apids(resp.json['apids'])
    apid_data = {'apids': apids, 'active_apids': active_apids}
    return apid_data


def get_unique_users(user_json, user_ids):
    """Get unique users"""
    ids = [u for u in user_json if u['user_id'] not in user_ids]
    return ids


@cmd('get-users')
@jsoncmd
def get_users(options):
    """Get all users for an app"""
    logger.info('Retrieving user_ids and saving to %s' % options.outfile)
    auth = (options.app_key, options.secret)
    index = 0
    increment = 10
    user_req = lambda ind, inc, auth: api_req('users/%d/%d' % (ind, inc), auth)
    resp = user_req(index, increment, auth)
    new_users = resp.json['users']
    users = new_users
    user_ids = [u['user_id'] for u in users]

    new_count = len(user_ids)
    logger.info('Retrieved %d new users' % new_count)

    while new_users:
        index += increment
        resp = user_req(index, increment, auth)
        # So unfortunately this endpoint doesn't act consistently upon
        # reaching the "end" of the user_ids associated with the app.
        # This means we have to check against the full list of user_ids
        new_users = get_unique_users(resp.json['users'], user_ids)
        users.extend(new_users)
        user_ids.extend([u['user_id'] for u in new_users])
        user_ids_count = len(user_ids)
        new_count = len(new_users)
        logger.info('Retrieved %d new users for a total of %d users' %
                    (new_count, user_ids_count))
    users_data = {'users': users}
    return users_data


@cmd('get-tags')
@jsoncmd
def get_tags(options)
    """Get all push tags associated with an app"""
    logger.info('Retrieving tags and saving to 
