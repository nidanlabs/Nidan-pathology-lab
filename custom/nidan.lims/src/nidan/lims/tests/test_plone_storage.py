import unittest

from nidan.lims.auth import build_user
from nidan.lims.persistence import PersistenceError
from nidan.lims.plone_storage import PloneRepository


class FakeObject(object):
    portal_type = "NIDANPatient"
    patient_id = "P-100"
    tenant_id = "lab-a"
    first_name = "Ravi"
    last_name = "Kumar"
    sex = "M"

    def getId(self):
        return "P-100"


class FakeContainer(object):
    def __init__(self, objects):
        self._objects = objects

    def values(self):
        return self._objects


class PloneStorageTests(unittest.TestCase):
    def setUp(self):
        self.user = build_user("u1", "lab-a", "owner@example.com", role="owner")
        self.repo = PloneRepository(FakeContainer([FakeObject()]))

    def test_get_is_tenant_scoped(self):
        record = self.repo.get(self.user, "lab-a", "patient", "P-100")
        self.assertEqual(record["tenant_id"], "lab-a")
        self.assertEqual(record["patient_id"], "P-100")

    def test_cross_tenant_read_is_rejected(self):
        with self.assertRaises(Exception):
            self.repo.get(self.user, "lab-b", "patient", "P-100")

    def test_unknown_record_type_is_rejected(self):
        with self.assertRaises(PersistenceError):
            self.repo._portal_type("invoice")


if __name__ == "__main__":
    unittest.main()
