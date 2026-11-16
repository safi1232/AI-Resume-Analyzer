
import streamlit as st
import requests


# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

API_URL = "https://ai-resume-analyzer-e130ba4c.fastapicloud.dev"


# =====================================
# HEADER
# =====================================

st.title("📄 AI Resume Analyzer")

st.write(
    "Analyze your resume against a job description "
    "using AI-powered extraction and a transparent "
    "100-point scoring system."
)

st.divider()


# =====================================
# INPUT SECTION
# =====================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("1. Upload Resume")

    uploaded_file = st.file_uploader(
        "Choose your resume (PDF)",
        type=["pdf"]
    )

with col2:

    st.subheader("2. Job Description")

    job_description = st.text_area(
        "Paste the job description",
        placeholder="Paste the complete job description here...",
        height=250
    )


# =====================================
# ANALYZE BUTTON
# =====================================

if st.button(
    "🚀 Analyze Resume",
    type="primary",
    use_container_width=True
):

    if uploaded_file is None:

        st.error("Please upload your resume.")

    elif not job_description.strip():

        st.error("Please provide a job description.")

    else:

        try:

            with st.spinner(
                "Analyzing your resume with AI..."
            ):

                files = {
                    "resume_file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf"
                    )
                }

                data = {
                    "job_description": job_description
                }

                response = requests.post(
                    f"{API_URL}/analyze",
                    files=files,
                    data=data,
                    timeout=180
                )

                response.raise_for_status()

                result = response.json()

            # =================================
            # VALIDATE API RESPONSE
            # =================================

            if not isinstance(result, dict):

                st.error("Invalid response received from API.")
                st.stop()

            if result.get("status") != "success":

                st.error(
                    result.get(
                        "message",
                        "Analysis failed."
                    )
                )

                st.stop()

            # =================================
            # SUCCESS MESSAGE
            # =================================

            st.success(
                result.get(
                    "message",
                    "Analysis completed successfully!"
                )
            )

            st.divider()

            st.header("📊 Resume Analysis Results")

            # =================================
            # OVERALL SCORE
            # =================================

            final_score = result.get("overall_score", 0)

            if not isinstance(final_score, (int, float)):

                st.error("Invalid overall score received from API.")
                st.stop()

            col1, col2 = st.columns([1, 2])

            with col1:

                st.metric(
                    "Overall Resume Score",
                    f"{final_score:.2f}/100"
                )

                st.progress(
                    min(max(float(final_score) / 100, 0), 1)
                )

            with col2:

                if final_score >= 80:

                    st.success("Strong job match!")

                elif final_score >= 60:

                    st.info(
                        "Good match, but improvements are needed."
                    )

                elif final_score >= 40:

                    st.warning(
                        "Moderate match. Several areas need improvement."
                    )

                else:

                    st.error(
                        "Low match. Significant improvements are needed."
                    )

            # =================================
            # ASSESSMENT COVERAGE
            # =================================

            coverage = result.get("assessment_coverage")

            if isinstance(coverage, (int, float)):

                st.metric(
                    "Assessment Coverage",
                    f"{coverage:.2f}%"
                )

                st.caption(
                    "Percentage of assessment categories successfully evaluated."
                )

            # =================================
            # SCORE BREAKDOWN
            # =================================

            st.divider()

            st.subheader("📈 Score Breakdown")

            breakdown = result.get(
                "score_breakdown", {}
            )

            status = result.get(
                "assessment_status", {}
            )

            score_items = [
                ("Skills", "skills", 35),
                ("Experience", "experience", 25),
                ("Education", "education", 15),
                ("Projects", "projects", 15),
                ("Keywords", "keywords", 10)
            ]

            columns = st.columns(5)

            for column, (label, key, maximum) in zip(
                columns,
                score_items
            ):

                with column:

                    category_data = breakdown.get(key, {})

                    if not isinstance(category_data, dict):
                        category_data = {}

                    weighted_score = category_data.get(
                        "weighted_score", 0
                    )

                    match_percentage = category_data.get(
                        "match_percentage"
                    )

                    if not isinstance(weighted_score, (int, float)):
                        weighted_score = 0

                    st.metric(
                        label,
                        f"{weighted_score:.2f}/{maximum}"
                    )

                    category_status = status.get(
                        key,
                        category_data.get("status", "assessed")
                    )

                    if category_status == "not_assessed":

                        st.caption("Not assessed")

                    elif category_status == "not_specified":

                        st.caption("Not specified")

                    elif isinstance(match_percentage, (int, float)):

                        st.caption(
                            f"Match: {match_percentage:.2f}%"
                        )

                    else:

                        st.caption("No match percentage available")

            # =================================
            # SKILLS ANALYSIS
            # =================================

            st.divider()

            st.subheader("🛠️ Skills Analysis")

            skills = result.get(
                "skills_analysis", {}
            )

            matched = skills.get(
                "matched_skills", []
            )

            missing = skills.get(
                "missing_skills", []
            )

            col1, col2 = st.columns(2)

            with col1:

                st.markdown(
                    f"**Matched Skills ({len(matched)})**"
                )

                if matched:

                    for skill in matched:

                        st.success(f"✓ {skill}")

                else:

                    st.write("No matched skills found.")

            with col2:

                st.markdown(
                    f"**Missing Skills ({len(missing)})**"
                )

                if missing:

                    for skill in missing:

                        st.warning(f"• {skill}")

                else:

                    st.write("No missing skills!")

            # =================================
            # AI FEEDBACK
            # =================================

            st.divider()

            st.subheader("🤖 AI Recommendations")

            feedback = result.get(
                "feedback",
                "No feedback available."
            )

            if isinstance(feedback, str):

                st.markdown(feedback)

            else:

                st.json(feedback)

            # =================================
            # RESUME INFORMATION
            # =================================

            st.divider()

            st.subheader("📄 Extracted Resume Information")

            resume = result.get(
                "resume_information", {}
            )

            if not isinstance(resume, dict):
                resume = {}

            with st.expander("Personal Information"):

                st.json({
                    "name": resume.get("name"),
                    "email": resume.get("email"),
                    "phone": resume.get("phone"),
                    "address": resume.get("address"),
                    "linkedin": resume.get("linkedin"),
                    "github": resume.get("github"),
                    "portfolio": resume.get("portfolio")
                })

            with st.expander("Skills"):

                st.write(
                    resume.get("skills") or []
                )

            with st.expander("Experience"):

                st.write(
                    resume.get("experience") or []
                )

            with st.expander("Education"):

                st.write(
                    resume.get("education") or []
                )

            with st.expander("Projects"):

                st.write(
                    resume.get("projects") or []
                )

            with st.expander("Certifications"):

                st.write(
                    resume.get("certifications") or []
                )

            # =================================
            # JOB INFORMATION
            # =================================

            st.divider()

            st.subheader("💼 Extracted Job Requirements")

            job = result.get(
                "job_information", {}
            )

            if not isinstance(job, dict):
                job = {}

            with st.expander("Job Details"):

                st.json(job)

            st.success(
                "Resume analysis completed successfully!"
            )

        # =================================
        # ERROR HANDLING
        # =================================

        except requests.exceptions.Timeout:

            st.error(
                "The API took too long to respond. Try again."
            )

        except requests.exceptions.ConnectionError:

            st.error(
                "Cannot connect to FastAPI. "
                "Please check your internet connection."
            )

        except requests.exceptions.HTTPError as e:

            st.error(
                f"API returned an error: {e}"
            )

            if e.response is not None:

                try:
                    st.json(e.response.json())

                except ValueError:
                    st.code(e.response.text)

        except requests.exceptions.RequestException as e:

            st.error(
                f"Request failed: {str(e)}"
            )

        except Exception as e:

            st.error(
                f"An unexpected error occurred: {str(e)}"
            )
