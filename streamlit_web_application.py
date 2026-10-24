import streamlit as st
from datetime import date
import validator
import database
import demo_data

st.set_page_config(
    page_title="AICTE Application Validation Assistant",
    page_icon="📋",
    layout="wide"
)

# Initialize local SQLite database
database.init_db()

# Clean, accessible styling (Blue, Teal, Saffron, and Crisp Neutral Dark Text)
st.markdown("""
<style>
    /* Global Text Contrast */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Ensure all Streamlit labels are dark and high-contrast */
    label, .stWidgetLabel, .stWidgetLabel p, .stMarkdown p {
        color: #0F172A !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
    }

    /* Radio button options visibility */
    div[role="radiogroup"] label {
        color: #1E293B !important;
        font-weight: 500 !important;
        margin-right: 1.25rem !important;
    }
    div[role="radiogroup"] p {
        color: #1E293B !important;
        font-weight: 500 !important;
    }

    /* Primary Heading */
    .main-title {
        color: #1E3A8A;
        font-size: 1.85rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #475569;
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }

    /* Persistent Prototype Disclaimer */
    .disclaimer-box {
        background-color: #EFF6FF;
        border-left: 4px solid #1E3A8A;
        padding: 0.85rem 1.2rem;
        border-radius: 4px;
        margin-bottom: 1.5rem;
        color: #1E3A8A;
        font-size: 0.88rem;
    }

    /* Section Subheadings */
    .section-header {
        color: #1E3A8A;
        font-size: 1.1rem;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 0.6rem;
        border-bottom: 2px solid #E2E8F0;
        padding-bottom: 0.3rem;
    }

    /* Comparison Table Styling */
    .matrix-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 0.8rem;
        margin-bottom: 1rem;
        background: #FFFFFF;
        border-radius: 6px;
        overflow: hidden;
        border: 1px solid #CBD5E1;
    }
    .matrix-table th {
        background-color: #0F766E;
        color: #FFFFFF !important;
        font-weight: 600;
        text-align: left;
        padding: 10px 14px;
        font-size: 0.88rem;
    }
    .matrix-table td {
        padding: 10px 14px;
        border-bottom: 1px solid #E2E8F0;
        color: #1E293B !important;
        font-size: 0.88rem;
    }
    .matrix-table tr:hover {
        background-color: #F1F5F9;
    }

    /* Status Badges */
    .badge-pass {
        background-color: #DCFCE7;
        color: #166534;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.82rem;
    }
    .badge-fail {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.82rem;
    }
    .badge-warning {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.82rem;
    }

    /* Warning Banner (Saffron) */
    .saffron-alert {
        background-color: #FFF7ED;
        border-left: 5px solid #EA580C;
        color: #9A3412;
        padding: 1rem;
        border-radius: 4px;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    /* Pass Banner */
    .teal-alert {
        background-color: #F0FDFA;
        border-left: 5px solid #0D9488;
        color: #115E59;
        padding: 1rem;
        border-radius: 4px;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    /* Save Button - Teal / Deep Blue instead of Red */
    div.stButton > button {
        background-color: #0F766E !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.65rem 1.8rem !important;
        width: 100% !important;
        font-size: 1rem !important;
        transition: 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        background-color: #115E59 !important;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# Header & Disclaimer
st.markdown('<div class="main-title">AICTE Application Validation Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Automated Document Verification Workspace (Prototype Validation Aid)</div>', unsafe_allow_html=True)

st.markdown("""
<div class="disclaimer-box">
    <strong>Student Prototype Notice:</strong> This assistant is an automated document validation aid for evaluation workflows only. 
    It is not affiliated with the official AICTE or any government ministry. It does not make final approval decisions or issue official government sanctions. Final approval remains strictly with a human reviewer.
</div>
""", unsafe_allow_html=True)

# Fixture / Demo Preset Selection
demo_options = list(demo_data.DEMO_CASES.keys()) if hasattr(demo_data, "DEMO_CASES") else ["Canonical Demo Case (Mismatched Name & Expired)"]
selected_preset = st.selectbox("Select Validation Scenario Preset", demo_options)

preset = demo_data.DEMO_CASES[selected_preset] if hasattr(demo_data, "DEMO_CASES") and selected_preset in demo_data.DEMO_CASES else {
    "app_inst": "Demo Institute of Technology",
    "app_ref": "NOC/DEMO/0001",
    "app_date": date(2026, 10, 24),
    "doc_inst": "Demo Institute of Tech. & Science",
    "doc_ref": "NOC/DEMO/0001",
    "doc_valid_until": date(2026, 3, 31)
}

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">1. Application Details (Portal Metadata)</div>', unsafe_allow_html=True)
    app_institution = st.text_input("Institution Name", value=preset.get("app_inst", "Demo Institute of Technology"))
    app_ref_no = st.text_input("NOC Reference Number", value=preset.get("app_ref", "NOC/DEMO/0001"))
    app_review_date = st.date_input("Application Review Date", value=preset.get("app_date", date(2026, 10, 24)))

with col2:
    st.markdown('<div class="section-header">2. Document Source (NOC Verification)</div>', unsafe_allow_html=True)
    doc_source = st.radio("Document Source", options=["Preloaded Demo NOC Data", "Upload Demo NOC PDF"], horizontal=True)

    if doc_source == "Upload Demo NOC PDF":
        uploaded_file = st.file_uploader("Upload Demo NOC PDF", type=["pdf"])
        if uploaded_file is not None:
            extracted = validator.extract_from_pdf(uploaded_file.read())
            doc_institution = extracted.get("institution_name", "")
            doc_ref_no = extracted.get("noc_reference", "")
            doc_valid_date = extracted.get("validity_date", date(2026, 3, 31))
        else:
            doc_institution = ""
            doc_ref_no = ""
            doc_valid_date = None
    else:
        st.info(f"Loaded: {selected_preset}")
        doc_institution = st.text_input("Document Institution Name", value=preset.get("doc_inst", "Demo Institute of Tech. & Science"))
        doc_ref_no = st.text_input("Document NOC Reference Number", value=preset.get("doc_ref", "NOC/DEMO/0001"))
        doc_valid_date = st.date_input("Document Validity Date", value=preset.get("doc_valid_until", date(2026, 3, 31)))

# Validation Execution
validation_result = validator.validate_application(
    app_institution=app_institution,
    app_ref=app_ref_no,
    app_review_date=app_review_date,
    doc_institution=doc_institution,
    doc_ref=doc_ref_no,
    doc_validity_date=doc_valid_date,
    doc_present=bool(doc_institution or doc_ref_no or doc_valid_date)
)

st.markdown('<div class="section-header">3. Side-by-Side Comparison & Discrepancy Matrix</div>', unsafe_allow_html=True)

# Overall Status Banner
if validation_result.get("status") == "Manual review required" or validation_result.get("flags"):
    st.markdown("""
    <div class="saffron-alert">
        ⚠️ <strong>STATUS: Manual review required</strong><br>
        One or more discrepancies detected during automated cross-referencing. Reviewer action is required.
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="teal-alert">
        ✅ <strong>STATUS: Automated Checks Passed</strong><br>
        All strict parameters match. Reviewer confirmation is still required before proceeding.
    </div>
    """, unsafe_allow_html=True)

# Discrepancy Matrix Table
name_status = '<span class="badge-fail">Mismatch</span>' if "Name mismatch" in validation_result.get("flags", []) else '<span class="badge-pass">Match</span>'
ref_status = '<span class="badge-fail">Mismatch</span>' if "Reference number mismatch" in validation_result.get("flags", []) else '<span class="badge-pass">Match</span>'
date_status = '<span class="badge-fail">Expired</span>' if "Expired document" in validation_result.get("flags", []) else '<span class="badge-pass">Valid</span>'

doc_date_str = doc_valid_date.strftime("%Y-%m-%d") if doc_valid_date else "Missing"
app_date_str = app_review_date.strftime("%Y-%m-%d") if app_review_date else "Missing"

matrix_html = f"""
<table class="matrix-table">
    <thead>
        <tr>
            <th>Field</th>
            <th>Application Value</th>
            <th>Document Value</th>
            <th>Status</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Institution Name</strong></td>
            <td>{app_institution}</td>
            <td>{doc_institution}</td>
            <td>{name_status}</td>
        </tr>
        <tr>
            <td><strong>NOC Reference Number</strong></td>
            <td>{app_ref_no}</td>
            <td>{doc_ref_no}</td>
            <td>{ref_status}</td>
        </tr>
        <tr>
            <td><strong>Document Validity Date</strong></td>
            <td>Review Date: {app_date_str}</td>
            <td>Valid Until: {doc_date_str}</td>
            <td>{date_status}</td>
        </tr>
    </tbody>
</table>
"""
st.markdown(matrix_html, unsafe_allow_html=True)

# Section 4: Reviewer Decision
st.markdown('<div class="section-header">4. Reviewer Decision & Record Persistence</div>', unsafe_allow_html=True)

col3, col4 = st.columns([1, 1])

with col3:
    reviewer_decision = st.radio(
        "Reviewer Decision",
        options=["Accept for review", "Request correction", "Escalate"],
        index=1
    )

with col4:
    default_comment = "Auto-flagged: " + ", ".join(validation_result.get("flags", [])) if validation_result.get("flags") else "Checks verified by reviewer."
    reviewer_comments = st.text_area(
        "Reviewer Comments",
        value=default_comment,
        height=100
    )

if st.button("💾 Save Review Decision to Database"):
    database.insert_review_decision(
        app_institution=app_institution,
        app_ref_number=app_ref_no,
        app_review_date=str(app_review_date),
        doc_source_type=doc_source,
        doc_institution=doc_institution,
        doc_ref_number=doc_ref_no,
        doc_validity_date=str(doc_valid_date) if doc_valid_date else None,
        flags=validation_result.get("flags", []),
        status=validation_result.get("status", "Manual review required"),
        reviewer_decision=reviewer_decision,
        reviewer_comments=reviewer_comments
    )
    st.success(f"Review decision '{reviewer_decision}' for {app_institution} successfully recorded into local SQLite database.")