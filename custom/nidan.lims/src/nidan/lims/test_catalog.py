"""NIDAN pathology test catalog foundation.

Reference intervals are intentionally stored as configurable data rather than
hard-coded clinical decisions. Labs must validate intervals against their
analyzers, methods, population and local policy before production use.
"""


TEST_CATALOG = {
    "CBC": {
        "name": "Complete Blood Count",
        "department": "Hematology",
        "sample_type": "EDTA",
        "parameters": [
            {"code": "HB", "name": "Hemoglobin", "unit": "g/dL", "result_type": "numeric"},
            {"code": "WBC", "name": "Total Leukocyte Count", "unit": "10^3/uL", "result_type": "numeric"},
            {"code": "RBC", "name": "Red Blood Cell Count", "unit": "10^6/uL", "result_type": "numeric"},
            {"code": "PLT", "name": "Platelet Count", "unit": "10^3/uL", "result_type": "numeric"},
            {"code": "HCT", "name": "Hematocrit", "unit": "%", "result_type": "numeric"},
            {"code": "MCV", "name": "Mean Corpuscular Volume", "unit": "fL", "result_type": "numeric"},
            {"code": "MCH", "name": "Mean Corpuscular Hemoglobin", "unit": "pg", "result_type": "numeric"},
            {"code": "MCHC", "name": "Mean Corpuscular Hb Concentration", "unit": "g/dL", "result_type": "numeric"},
            {"code": "RDW_CV", "name": "RDW-CV", "unit": "%", "result_type": "numeric"},
        ],
    },
    "LFT": {
        "name": "Liver Function Test",
        "department": "Biochemistry",
        "sample_type": "SERUM",
        "parameters": [
            {"code": "TBIL", "name": "Total Bilirubin", "unit": "mg/dL", "result_type": "numeric"},
            {"code": "DBIL", "name": "Direct Bilirubin", "unit": "mg/dL", "result_type": "numeric"},
            {"code": "ALT", "name": "ALT (SGPT)", "unit": "U/L", "result_type": "numeric"},
            {"code": "AST", "name": "AST (SGOT)", "unit": "U/L", "result_type": "numeric"},
            {"code": "ALP", "name": "Alkaline Phosphatase", "unit": "U/L", "result_type": "numeric"},
            {"code": "TP", "name": "Total Protein", "unit": "g/dL", "result_type": "numeric"},
            {"code": "ALB", "name": "Albumin", "unit": "g/dL", "result_type": "numeric"},
        ],
    },
    "RFT": {
        "name": "Renal Function Test",
        "department": "Biochemistry",
        "sample_type": "SERUM",
        "parameters": [
            {"code": "UREA", "name": "Blood Urea", "unit": "mg/dL", "result_type": "numeric"},
            {"code": "CREAT", "name": "Creatinine", "unit": "mg/dL", "result_type": "numeric"},
            {"code": "URIC", "name": "Uric Acid", "unit": "mg/dL", "result_type": "numeric"},
            {"code": "SOD", "name": "Sodium", "unit": "mmol/L", "result_type": "numeric"},
            {"code": "POT", "name": "Potassium", "unit": "mmol/L", "result_type": "numeric"},
        ],
    },
    "LIPID": {
        "name": "Lipid Profile",
        "department": "Biochemistry",
        "sample_type": "SERUM",
        "parameters": [
            {"code": "TC", "name": "Total Cholesterol", "unit": "mg/dL", "result_type": "numeric"},
            {"code": "TG", "name": "Triglycerides", "unit": "mg/dL", "result_type": "numeric"},
            {"code": "HDL", "name": "HDL Cholesterol", "unit": "mg/dL", "result_type": "numeric"},
            {"code": "LDL", "name": "LDL Cholesterol", "unit": "mg/dL", "result_type": "numeric"},
        ],
    },
    "TSH": {
        "name": "Thyroid Stimulating Hormone",
        "department": "Immunoassay",
        "sample_type": "SERUM",
        "parameters": [
            {"code": "TSH", "name": "TSH", "unit": "uIU/mL", "result_type": "numeric"},
        ],
    },
    "WIDAL": {
        "name": "Widal Test",
        "department": "Serology",
        "sample_type": "SERUM",
        "parameters": [
            {"code": "TO", "name": "Salmonella Typhi O", "unit": "titer", "result_type": "text"},
            {"code": "TH", "name": "Salmonella Typhi H", "unit": "titer", "result_type": "text"},
            {"code": "AH", "name": "Salmonella Paratyphi A H", "unit": "titer", "result_type": "text"},
            {"code": "BH", "name": "Salmonella Paratyphi B H", "unit": "titer", "result_type": "text"},
        ],
    },
    "ESR": {
        "name": "Erythrocyte Sedimentation Rate",
        "department": "Hematology",
        "sample_type": "EDTA",
        "parameters": [
            {"code": "ESR", "name": "ESR", "unit": "mm/hr", "result_type": "numeric"},
        ],
    },
}


def get_test(code):
    """Return a test definition or None for an unknown code."""
    return TEST_CATALOG.get(code.upper())


def list_parameters(code):
    """Return parameter definitions for a test code."""
    test = get_test(code)
    return [] if test is None else list(test["parameters"])
