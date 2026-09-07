import unittest

from nidan.lims.api_endpoints import create_patient_payload, create_sample_payload
from nidan.lims.auth import build_user
from nidan.lims.permissions import PermissionError


class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.owner = build_user("U1", "LAB-1", "owner@test", role="owner")
        self.tech = build_user("U2", "LAB-1", "tech@test", role="technician")

    def test_owner_can_create_patient(self):
        patient = {
            "patient_id": "P1", "first_name": "A", "last_name": "B",
            "sex": "M",
        }
        result = create_patient_payload(self.owner, "LAB-1", patient)
        self.assertEqual("nidan.patient", result["type"])
        self.assertEqual("LAB-1", result["tenant_id"])

    def test_owner_can_create_sample(self):
        sample = {
            "sample_id": "S1", "patient_id": "P1", "sample_type": "SERUM",
            "status": "registered",
        }
        result = create_sample_payload(self.owner, "LAB-1", sample)
        self.assertEqual("nidan.sample", result["type"])

    def test_technician_cannot_create_patient(self):
        with self.assertRaises(PermissionError):
            create_patient_payload(self.tech, "LAB-1", {
                "patient_id": "P1", "first_name": "A", "last_name": "B", "sex": "M"
            })


if __name__ == "__main__":
    unittest.main()
