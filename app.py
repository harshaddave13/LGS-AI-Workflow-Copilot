import streamlit as st

from backend.pdf_parser import extract_text_from_pdf
from backend.extractor import extract_lgs_requirements
from backend.evidence import find_evidence
from backend.review import init_db, save_review, get_reviews


# ============================================================
# INITIAL SETUP
# ============================================================

init_db()

st.set_page_config(
    page_title="LGS AI Workflow Copilot",
    page_icon="🏗️",
    layout="wide"
)

st.title("LGS AI Workflow Copilot")

st.caption(
    "AI-assisted requirement extraction and scoping "
    "for Light Gauge Steel construction projects"
)


# ============================================================
# FILE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "Upload a construction specification PDF",
    type=["pdf"]
)


# ============================================================
# MAIN WORKFLOW
# Everything that depends on the uploaded PDF stays in here.
# ============================================================

if uploaded_file:

    # ========================================================
    # STEP 1: EXTRACT PDF TEXT
    # ========================================================

    with st.spinner("Processing document..."):
        pages = extract_text_from_pdf(uploaded_file)

    st.success(
        f"Successfully processed {len(pages)} page(s)"
    )

    full_text = "\n".join(
        page["text"] for page in pages
    )


    # ========================================================
    # STEP 2: EXTRACT LGS REQUIREMENTS
    # ========================================================

    requirements = extract_lgs_requirements(full_text)


    # ========================================================
    # STEP 3: FIND SOURCE EVIDENCE
    # ========================================================

    evidence = {}

    for field in [
        "fire_rating",
        "acoustic_rating",
        "steel_thickness",
        "stud_spacing",
        "wall_height"
    ]:
        evidence[field] = find_evidence(
            pages,
            requirements.get(field)
        )


    # ========================================================
    # STEP 4: DISPLAY EXTRACTED REQUIREMENTS
    # ========================================================

    st.divider()

    st.subheader("LGS Requirement Extraction")

    st.caption(
        "Key project requirements automatically extracted "
        "from the uploaded construction specification."
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "System Type",
            requirements.get("system_type")
            or "Not identified"
        )

        st.metric(
            "Fire Rating",
            requirements.get("fire_rating")
            or "Missing"
        )

        st.metric(
            "Acoustic Rating",
            requirements.get("acoustic_rating")
            or "Missing"
        )

    with col2:

        st.metric(
            "Steel Thickness",
            requirements.get("steel_thickness")
            or "Missing"
        )

        st.metric(
            "Stud Spacing",
            requirements.get("stud_spacing")
            or "Missing"
        )

        st.metric(
            "Wall Height",
            requirements.get("wall_height")
            or "Missing"
        )


    # ========================================================
    # STEP 5: FLAG MISSING INFORMATION
    # ========================================================

    missing_information = requirements.get(
        "missing_information",
        []
    )

    if missing_information:

        readable_missing = [
            item.replace("_", " ").title()
            for item in missing_information
        ]

        st.warning(
            "Missing or unclear information: "
            + ", ".join(readable_missing)
        )

    else:

        st.success(
            "All key scoping fields identified."
        )


    # ========================================================
    # STEP 6: SOURCE EVIDENCE
    # ========================================================

    st.divider()

    st.subheader("Source Evidence")

    st.caption(
        "Review the source text supporting each "
        "automatically extracted value."
    )

    field_labels = {
        "fire_rating": "Fire Rating",
        "acoustic_rating": "Acoustic Rating",
        "steel_thickness": "Steel Thickness",
        "stud_spacing": "Stud Spacing",
        "wall_height": "Wall Height"
    }

    for field, label in field_labels.items():

        value = requirements.get(field)

        if not value:
            continue

        item = evidence.get(field)

        with st.expander(
            f"{label}: {value}"
        ):

            if item:

                st.write(
                    f"**Source page:** {item['page']}"
                )

                st.info(
                    item["evidence"]
                )

            else:

                st.warning(
                    "Supporting evidence could not "
                    "be located automatically."
                )


    # ========================================================
    # STEP 7: HUMAN-IN-THE-LOOP REVIEW
    # ========================================================

    st.divider()

    st.subheader("Human Review")

    st.caption(
        "An estimator or engineer can approve, edit, "
        "or reject AI-extracted requirements before "
        "they enter the project workflow."
    )

    review_fields = {
        "fire_rating": "Fire Rating",
        "acoustic_rating": "Acoustic Rating",
        "steel_thickness": "Steel Thickness",
        "stud_spacing": "Stud Spacing",
        "wall_height": "Wall Height"
    }

    for field, label in review_fields.items():

        original_value = requirements.get(field)

        st.markdown(f"### {label}")

        reviewed_value = st.text_input(
            f"Reviewed value for {label}",
            value=original_value or "",
            key=f"review_value_{field}"
        )

        col_approve, col_edit, col_reject = st.columns(3)

        with col_approve:

            if st.button(
                "Approve",
                key=f"approve_{field}",
                use_container_width=True
            ):

                save_review(
                    field_name=field,
                    original_value=original_value,
                    reviewed_value=reviewed_value,
                    status="approved"
                )

                st.success(
                    f"{label} approved."
                )

        with col_edit:

            if st.button(
                "Save Edit",
                key=f"edit_{field}",
                use_container_width=True
            ):

                save_review(
                    field_name=field,
                    original_value=original_value,
                    reviewed_value=reviewed_value,
                    status="edited"
                )

                st.info(
                    f"{label} correction saved."
                )

        with col_reject:

            if st.button(
                "Reject",
                key=f"reject_{field}",
                use_container_width=True
            ):

                save_review(
                    field_name=field,
                    original_value=original_value,
                    reviewed_value=reviewed_value,
                    status="rejected"
                )

                st.warning(
                    f"{label} rejected."
                )


    # ========================================================
    # STEP 8: HUMAN REVIEW DASHBOARD
    # ========================================================

    st.divider()

    st.subheader("Human Review Dashboard")

    st.caption(
        "Summary of expert decisions recorded during "
        "the AI-assisted review workflow."
    )

    reviews = get_reviews()

    if reviews:

        total_reviews = len(reviews)

        approved = sum(
            1 for review in reviews
            if review[4] == "approved"
        )

        edited = sum(
            1 for review in reviews
            if review[4] == "edited"
        )

        rejected = sum(
            1 for review in reviews
            if review[4] == "rejected"
        )

        intervention_rate = (
            ((edited + rejected) / total_reviews) * 100
            if total_reviews > 0
            else 0
        )

        metric1, metric2, metric3, metric4, metric5 = st.columns(5)

        with metric1:
            st.metric(
                "Total Reviews",
                total_reviews
            )

        with metric2:
            st.metric(
                "Approved",
                approved
            )

        with metric3:
            st.metric(
                "Edited",
                edited
            )

        with metric4:
            st.metric(
                "Rejected",
                rejected
            )

        with metric5:
            st.metric(
                "Human Intervention",
                f"{intervention_rate:.1f}%"
            )

        st.subheader("Review History")

        review_data = []

        for review in reviews:

            review_data.append({
                "Field": review[1]
                .replace("_", " ")
                .title(),

                "AI Value": review[2],

                "Human Value": review[3],

                "Decision": review[4].title(),

                "Timestamp": review[5]
            })

        st.dataframe(
            review_data,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No human review decisions recorded yet."
        )


    # ========================================================
    # STEP 9: SOURCE DOCUMENT
    # ========================================================

    st.divider()

    st.subheader("Source Document")

    st.caption(
        "Extracted page text from the uploaded PDF."
    )

    for page in pages:

        with st.expander(
            f"Page {page['page']}",
            expanded=False
        ):

            st.text_area(
                f"Extracted text - Page {page['page']}",
                page["text"],
                height=250,
                key=f"page_{page['page']}"
            )


# ============================================================
# EMPTY STATE
# ============================================================

else:

    st.info(
        "Upload a construction specification PDF "
        "to begin the LGS scoping workflow."
    )