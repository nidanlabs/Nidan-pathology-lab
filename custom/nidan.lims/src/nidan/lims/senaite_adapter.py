"""Small integration boundary between NIDAN domain logic and SENAITE.

The adapter intentionally depends on plain mappings. SENAITE/Plone content
objects can be passed in by a future browser view, subscriber, or API layer
without coupling the domain helpers to a specific Zope request context.
"""


class SENAITEAdapter(object):
    """Translate NIDAN workflow data into SENAITE-friendly records."""

    def patient_payload(self, patient):
        return {
            "patient_id": patient.get("patient_id"),
            "first_name": patient.get("first_name"),
            "last_name": patient.get("last_name"),
            "date_of_birth": patient.get("date_of_birth"),
            "sex": patient.get("sex"),
            "phone": patient.get("phone", ""),
            "address": patient.get("address", ""),
        }

    def sample_payload(self, sample):
        return {
            "sample_id": sample.get("sample_id"),
            "patient_id": sample.get("patient_id"),
            "sample_type": sample.get("sample_type"),
            "status": sample.get("status", "registered"),
            "collection_date": sample.get("collection_date"),
        }

    def result_payload(self, result):
        return {
            "test_code": result.get("test_code"),
            "parameters": list(result.get("parameters", [])),
            "state": result.get("state", "draft"),
        }

    def report_payload(self, report):
        return {
            "report_id": report.get("report_id"),
            "patient": dict(report.get("patient", {})),
            "sample": dict(report.get("sample", {})),
            "results": list(report.get("results", [])),
            "state": report.get("state", "draft"),
            "remarks": report.get("remarks", ""),
        }
