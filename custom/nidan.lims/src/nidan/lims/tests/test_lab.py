import unittest

from nidan.lims.lab import LabError, register_lab, update_lab_settings


class TestLab(unittest.TestCase):
    def test_register_lab(self):
        lab = register_lab(
            "LAB-001", "Nidan Pathology Lab", "owner@example.com", "+91-9999999999"
        )
        self.assertEqual("LAB-001", lab["tenant_id"])
        self.assertEqual("trial", lab["status"])
        self.assertEqual("INR", lab["currency"])
        self.assertEqual("Asia/Kolkata", lab["timezone"])

    def test_phone_required(self):
        with self.assertRaises(LabError):
            register_lab("LAB-001", "Demo", "owner@example.com")

    def test_update_settings(self):
        lab = register_lab("LAB-001", "Demo", "owner@example.com", "123")
        updated = update_lab_settings(lab, address="Raigarh, Chhattisgarh")
        self.assertEqual("Raigarh, Chhattisgarh", updated["address"])

    def test_protected_settings_are_rejected(self):
        lab = register_lab("LAB-001", "Demo", "owner@example.com", "123")
        with self.assertRaises(LabError):
            update_lab_settings(lab, plan="premium")


if __name__ == "__main__":
    unittest.main()
