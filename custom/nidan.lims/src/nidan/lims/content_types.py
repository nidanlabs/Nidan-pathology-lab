"""Dexterity-ready content type metadata for NIDAN.

The domain interfaces remain the source of field contracts. This module
provides the stable portal type identifiers and interface mapping used by a
Plone integration profile.
"""

from nidan.lims.interfaces import INIDANPatient, INIDANSample, INIDANReport


CONTENT_TYPE_INTERFACES = {
    "NIDAN Patient": INIDANPatient,
    "NIDAN Sample": INIDANSample,
    "NIDAN Report": INIDANReport,
}


def get_interface(portal_type):
    """Return the schema interface for a supported portal type."""
    try:
        return CONTENT_TYPE_INTERFACES[portal_type]
    except KeyError:
        raise ValueError("Unknown NIDAN portal type: %s" % portal_type)
