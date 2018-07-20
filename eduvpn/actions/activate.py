# python-eduvpn-client - The GNU/Linux eduVPN client and Python API
#
# Copyright: 2017, The Commons Conservancy eduVPN Programme
# SPDX-License-Identifier: GPL-3.0+

import logging
import gi
from gi.repository import GLib
from eduvpn.util import error_helper, thread_helper
from eduvpn.oauth2 import oauth_from_token
from eduvpn.manager import update_config_provider, update_keys_provider, connect_provider
from eduvpn.remote import get_profile_config, create_keypair, user_info, check_certificate
from eduvpn.steps.reauth import reauth
from eduvpn.notify import notify
from eduvpn.openvpn import parse_ovpn
from eduvpn.exceptions import EduvpnAuthException, EduvpnException
from eduvpn.crypto import common_name_from_cert

logger = logging.getLogger(__name__)


# ui thread
def activate_connection(meta, builder, verifier):
    """do the actual connecting action"""
    logger.info("Connecting to {}".format(meta.display_name))
    notify("eduVPN connecting...", "Connecting to '{}'".format(meta.display_name))
    try:
        if not meta.token:
            logger.error("metadata for {} doesn't contain oauth2 token".format(meta.uuid))
            connect_provider(meta.uuid)

        else:
            oauth = oauth_from_token(meta=meta)
            thread_helper(lambda: _quick_check(oauth, meta, verifier, builder))

    except Exception as e:
        switch = builder.get_object('connect-switch')
        GLib.idle_add(switch.set_active, False)
        window = builder.get_object('eduvpn-window')
        error_helper(window, "can't enable connection", "{}: {}".format(type(e).__name__, str(e)))
        raise


def _quick_check(oauth, meta, verifier, builder):
    """quickly see if the can fetch messages, otherwise reauth"""
    try:
        user_info(oauth, meta.api_base_uri)
        _connect(oauth, meta)
    except EduvpnAuthException:
        GLib.idle_add(lambda: reauth(meta=meta, verifier=verifier, builder=builder))
    except Exception as e:
        error = e
        window = builder.get_object('eduvpn-window')
        GLib.idle_add(lambda: error_helper(window, "Can't check account status", "{}".format(str(error))))
        raise


def _connect(oauth, meta):
    config = get_profile_config(oauth, meta.api_base_uri, meta.profile_id)
    meta.config = config
    config_dict = parse_ovpn(meta.config)
    update_config_provider(meta, config_dict)

    common_name = common_name_from_cert(meta.cert.encode('ascii'))

    cert_valid = check_certificate(oauth, meta.api_base_uri, common_name)

    if not cert_valid['is_valid']:
        logger.warning('client certificate not valid, reason: {}'.format(cert_valid['reason']))
        if cert_valid['reason'] in ('certificate_missing', 'certificate_not_yet_valid', 'certificate_expired'):
            logger.info('Going to try to fetch new keypair')
            cert, key = create_keypair(oauth, meta.api_base_uri)
            update_keys_provider(meta.uuid, cert, key)
        elif cert_valid['reason'] == 'user_disabled':
            raise EduvpnException('Your account has been disabled.')
        else:
            raise EduvpnException('Your client certificate is invalid ({})'.format(cert_valid['reason']))

    connect_provider(meta.uuid)
