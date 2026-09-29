from __future__ import annotations

import base64
import html
from datetime import date

import requests
import streamlit as st


# ==========================================
# Page configuration
# ==========================================

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)


# ==========================================
# Configuration
# ==========================================

BACKEND_URL = (
    st.secrets.get(
        "BACKEND_URL",
        "http://127.0.0.1:8000",
    )
    .rstrip("/")
)


# ==========================================
# Session state
# ==========================================

if "document" not in st.session_state:
    st.session_state.document = ""


# ==========================================
# API helper
# ==========================================

def post(
    path: str,
    payload: dict,
):
    """
    Send a POST request to FastAPI.
    """

    return requests.post(
        f"{BACKEND_URL}{path}",
        json=payload,
        timeout=120,
    )


# ==========================================
# Preview helper
# ==========================================

def preview(text: str):
    """
    Display generated document safely.
    """

    safe_text = html.escape(text)

    st.markdown(
        f"""
        <div
            style="
                background:#111827;
                color:#f9fafb;
                border:1px solid #374151;
                border-radius:12px;
                padding:22px;
                max-height:620px;
                overflow-y:auto;
                white-space:pre-wrap;
                font-family:Georgia,serif;
                line-height:1.65;
            "
        >
            {safe_text}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================
# Header
# ==========================================

st.title("⚖️ LegalEase")

st.caption(
    "AI-powered legal document drafting • "
    "editable • TXT / DOCX / PDF"
)

st.warning(
    "LegalEase creates AI-generated drafts, "
    "not legal advice. Review the document "
    "carefully before using or signing it."
)


# ==========================================
# Sidebar
# ==========================================

with st.sidebar:

    st.header("Document Details")

    document_type = st.selectbox(
        "Document type",
        [
            "Employment Contract",
            "Non-Disclosure Agreement (NDA)",
            "Residential Lease Agreement",
            "Employment Offer Letter",
            "Freelance Work Contract",
            "Service Agreement",
            "General Agreement",
            "Custom Legal Document",
        ],
    )

    if document_type == "Custom Legal Document":

        document_type = st.text_input(
            "Custom document type",
            value="Legal Agreement",
        )

    parties = st.text_area(
        "Parties involved",
        placeholder=(
            "Jane Doe (Service Provider); "
            "TechNova Inc. (Client)"
        ),
        height=110,
    )

    terms = st.text_area(
        "Terms & Conditions",
        placeholder=(
            "Payment within 30 days; "
            "Confidentiality must be maintained; "
            "Either party may terminate with 15 days notice"
        ),
        height=160,
        help=(
            "Separate terms using semicolons."
        ),
    )

    effective_date = st.date_input(
        "Effective date",
        value=date.today(),
    )

    language = st.selectbox(
        "Output language",
        [
            "English",
            "Tamil",
            "Hindi",
            "Malayalam",
            "Telugu",
            "Kannada",
        ],
    )

    logo = st.file_uploader(
        "Optional company logo",
        type=[
            "png",
            "jpg",
            "jpeg",
        ],
        help=(
            "Used in DOCX/PDF exports."
        ),
    )

    generate = st.button(
        "Generate Document",
        type="primary",
        use_container_width=True,
    )


# ==========================================
# Generate document
# ==========================================

if generate:

    if not parties.strip():

        st.error(
            "Please enter the parties involved."
        )

    elif not terms.strip():

        st.error(
            "Please enter at least one term."
        )

    else:

        payload = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "dates": effective_date.isoformat(),
            "language": language,
        }

        try:

            with st.spinner(
                "Generating your legal draft..."
            ):

                response = post(
                    "/generate",
                    payload,
                )

            if response.ok:

                data = response.json()

                st.session_state.document = (
                    data["content"]
                )

                if data["mode"] == "gemini":

                    st.success(
                        "Document generated using Gemini."
                    )

                else:

                    st.info(
                        "Demo document generated. "
                        "Add GEMINI_API_KEY to enable "
                        "Gemini generation."
                    )

            else:

                try:
                    detail = response.json().get(
                        "detail",
                        response.text,
                    )

                except Exception:
                    detail = response.text

                st.error(
                    f"Backend error: {detail}"
                )

        except requests.RequestException as exc:

            st.error(
                "Could not reach FastAPI backend.\n\n"
                f"Backend: {BACKEND_URL}\n\n"
                f"Error: {exc}"
            )


# ==========================================
# Generated document
# ==========================================

st.divider()


if st.session_state.document:

    left, right = st.columns(
        [1.1, 1]
    )

    # --------------------------------------
    # Preview
    # --------------------------------------

    with left:

        st.subheader("Document Preview")

        preview(
            st.session_state.document
        )

    # --------------------------------------
    # Editor
    # --------------------------------------

    with right:

        st.subheader(
            "Edit Document"
        )

        edited_document = st.text_area(
            "Document text",
            value=st.session_state.document,
            height=620,
            label_visibility="collapsed",
        )

        st.session_state.document = (
            edited_document
        )

    # --------------------------------------
    # Download
    # --------------------------------------

    st.subheader("Download")

    if logo:

        logo_base64 = base64.b64encode(
            logo.getvalue()
        ).decode("ascii")

    else:

        logo_base64 = None

    export_payload = {
        "document_type": document_type,
        "content": st.session_state.document,
        "terms": terms,
        "logo_base64": logo_base64,
    }

    txt_col, docx_col, pdf_col = st.columns(3)

    # TXT
    with txt_col:

        if st.button(
            "Prepare TXT",
            use_container_width=True,
        ):

            try:

                response = post(
                    "/export/txt",
                    export_payload,
                )

                if response.ok:

                    st.download_button(
                        "Save TXT",
                        data=response.content,
                        file_name=(
                            "legalease-document.txt"
                        ),
                        mime=(
                            "text/plain"
                        ),
                        use_container_width=True,
                    )

                else:

                    st.error(
                        response.text
                    )

            except requests.RequestException as exc:

                st.error(
                    f"Export failed: {exc}"
                )

    # DOCX
    with docx_col:

        if st.button(
            "Prepare DOCX",
            use_container_width=True,
        ):

            try:

                response = post(
                    "/export/docx",
                    export_payload,
                )

                if response.ok:

                    st.download_button(
                        "Save DOCX",
                        data=response.content,
                        file_name=(
                            "legalease-document.docx"
                        ),
                        mime=(
                            "application/"
                            "vnd.openxmlformats-officedocument."
                            "wordprocessingml.document"
                        ),
                        use_container_width=True,
                    )

                else:

                    st.error(
                        response.text
                    )

            except requests.RequestException as exc:

                st.error(
                    f"Export failed: {exc}"
                )

    # PDF
    with pdf_col:

        if st.button(
            "Prepare PDF",
            use_container_width=True,
        ):

            try:

                response = post(
                    "/export/pdf",
                    export_payload,
                )

                if response.ok:

                    st.download_button(
                        "Save PDF",
                        data=response.content,
                        file_name=(
                            "legalease-document.pdf"
                        ),
                        mime="application/pdf",
                        use_container_width=True,
                    )

                else:

                    st.error(
                        response.text
                    )

            except requests.RequestException as exc:

                st.error(
                    f"Export failed: {exc}"
                )

    st.info(
        "After editing the document, export it again "
        "to ensure the latest version is downloaded."
    )

else:

    st.info(
        "Enter the document details in the sidebar "
        "and click Generate Document."
    )