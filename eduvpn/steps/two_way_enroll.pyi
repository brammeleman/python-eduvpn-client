from eduvpn.metadata import Metadata

def two_fa_enroll_window(builder, oauth, meta: Metadata, config_dict: dict, secret=None): ...
def _background(builder, oauth, meta: Metadata, config_dict: dict, secret=None): ...
def _step2(builder, oauth, meta: Metadata, config_dict: dict, secret): ...