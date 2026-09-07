"""Dexterity schema contracts for the NIDAN content types."""

from zope import schema
from zope.interface import Interface


class INIDANPatient(Interface):
    tenant_id = schema.TextLine(title=u"Tenant ID", required=True)
    patient_id = schema.TextLine(title=u"Patient ID", required=True)
    first_name = schema.TextLine(title=u"First Name", required=True)
    last_name = schema.TextLine(title=u"Last Name", required=True)
    date_of_birth = schema.Date(title=u"Date of Birth", required=False)
    sex = schema.Choice(title=u"Sex", values=(u"M", u"F", u"O"), required=True)
    phone = schema.TextLine(title=u"Phone", required=False)
    address = schema.Text(title=u"Address", required=False)
    referring_doctor_id = schema.TextLine(title=u"Referring Doctor ID", required=False)


class INIDANSample(Interface):
    tenant_id = schema.TextLine(title=u"Tenant ID", required=True)
    sample_id = schema.TextLine(title=u"Sample ID", required=True)
    patient_id = schema.TextLine(title=u"Patient ID", required=True)
    sample_type = schema.TextLine(title=u"Sample Type", required=True)
    status = schema.Choice(
        title=u"Status",
        values=(u"registered", u"collected", u"received", u"processing", u"completed", u"rejected"),
        required=True,
    )
    collection_date = schema.Date(title=u"Collection Date", required=False)


class INIDANReport(Interface):
    tenant_id = schema.TextLine(title=u"Tenant ID", required=True)
    report_id = schema.TextLine(title=u"Report ID", required=True)
    patient_id = schema.TextLine(title=u"Patient ID", required=True)
    sample_id = schema.TextLine(title=u"Sample ID", required=True)
    state = schema.Choice(title=u"Report State", values=(u"draft", u"verified", u"released"), required=True)
    remarks = schema.Text(title=u"Remarks", required=False)
