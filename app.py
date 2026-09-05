import streamlit as st
import time
import re
import streamlit.components.v1 as components

from resume_parser import extract_text_from_resume
from skill_extractor import extract_skills


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Interviewer",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# SESSION STATE
# =========================================================

if "started" not in st.session_state:
    st.session_state.started = False

if "finished" not in st.session_state:
    st.session_state.finished = False

if "candidate_name" not in st.session_state:
    st.session_state.candidate_name = ""

if "role" not in st.session_state:
    st.session_state.role = ""

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "skills" not in st.session_state:
    st.session_state.skills = []

if "resume_analysis" not in st.session_state:
    st.session_state.resume_analysis = {}

if "questions" not in st.session_state:
    st.session_state.questions = []

if "current_question" not in st.session_state:
    st.session_state.current_question = 0

if "answers" not in st.session_state:
    st.session_state.answers = []

if "scores" not in st.session_state:
    st.session_state.scores = []

if "feedback" not in st.session_state:
    st.session_state.feedback = []

if "evaluations" not in st.session_state:
    st.session_state.evaluations = []

if "celebrated" not in st.session_state:
    st.session_state.celebrated = False

if "question_started_at" not in st.session_state:
    st.session_state.question_started_at = None

if "question_times" not in st.session_state:
    st.session_state.question_times = []


# =========================================================
# LIGHT PINK / PISTA THEME
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            linear-gradient(
                rgba(255, 239, 246, 0.92),
                rgba(248, 244, 230, 0.95)
            ),
            url("https://images.unsplash.com/photo-1497250681960-ef046c08a56e?auto=format&fit=crop&w=1800&q=75");

        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    h1, h2, h3 {
        color: #28152f !important;
    }

    .brand {
        font-size: 38px;
        font-weight: 800;
        color: #29152f;
        letter-spacing: -1px;
    }

    .brand span {
        color: #f52b82;
    }

    .subtitle {
        color: #6d5c69;
        font-size: 17px;
    }

    .small-label {
        color: #765d70;
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .feature-title {
        font-weight: 800;
        color: #29152f;
        font-size: 18px;
    }

    .feature-text {
        color: #6d5c69;
        line-height: 1.5;
    }

    .score-number {
        font-size: 64px;
        font-weight: 800;
        color: #f72d83;
        text-align: center;
        margin: 0;
    }

    .score-caption {
        text-align: center;
        color: #6d5c69;
        font-size: 16px;
    }

    .conversation-title {
        color: #29152f;
        font-size: 22px;
        font-weight: 800;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.9);
        background: rgba(255, 255, 255, 0.82);
        box-shadow: 0 12px 35px rgba(104, 62, 87, 0.10);
    }

    .stButton > button {
        border-radius: 18px;
        border: none;
        background: #f72d83;
        color: white;
        font-weight: 700;
        font-size: 16px;
        padding: 0.65rem 1.3rem;
        box-shadow: 0 7px 18px rgba(247, 45, 131, 0.25);
    }

    .stButton > button:hover {
        background: #e91d72;
        color: white;
    }

    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] {
        border-radius: 16px !important;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# INTERVIEW QUESTIONS
# =========================================================

ROLE_QUESTIONS = {

    "AI / ML Engineer": [
        "Tell me about yourself and your experience with Artificial Intelligence or Machine Learning.",
        "Explain one Machine Learning project you have worked on. What problem were you solving?",
        "What is the difference between supervised and unsupervised learning?",
        "How would you evaluate the performance of a classification model?",
        "Tell me about a difficult technical problem you faced and how you solved it."
    ],

    "Data Scientist": [
        "Tell me about yourself and your experience with Data Science.",
        "Describe a data analysis or machine learning project you have worked on.",
        "How do you handle missing values in a dataset?",
        "What is the difference between classification and regression?",
        "How would you explain a machine learning model's results to a non-technical person?"
    ],

    "Python Developer": [
        "Tell me about yourself and your Python development experience.",
        "Describe a Python project you have worked on.",
        "What is the difference between a list, tuple and dictionary in Python?",
        "How do you handle errors and exceptions in Python?",
        "Tell me about a challenging coding problem you solved."
    ],

    "Software Developer": [
        "Tell me about yourself and your software development experience.",
        "Describe one software project you have worked on.",
        "How do you approach debugging a program?",
        "What is version control and why is Git useful?",
        "Tell me about a technical challenge you faced and how you solved it."
    ]
}


# =========================================================
# INTERVIEW BUDDY
# =========================================================

def show_interview_buddy(message, mood="friendly"):

    if mood == "happy":
        icon = "🐶"

    elif mood == "celebrate":
        icon = "🎉"

    else:
        icon = "🐱"

    st.info(
        f"{icon} **Interview Buddy**\n\n"
        f"{message}"
    )


# =========================================================
# RESUME ANALYSIS
# =========================================================

def get_resume_summary(resume_text):
    clean_text = re.sub(r"\s+", " ", resume_text).strip()

    if not clean_text:
        return "No readable text was found in the uploaded resume."

    sentences = re.split(r"(?<=[.!?])\s+", clean_text)

    useful_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence.split()) >= 8:
            useful_sentences.append(sentence)

    if useful_sentences:
        summary = " ".join(useful_sentences[:3])
    else:
        summary = clean_text[:500]

    return summary[:700]


def extract_resume_projects_experience(resume_text):
    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in resume_text.splitlines()
    ]

    lines = [
        line for line in lines
        if len(line) >= 12 and len(line.split()) >= 3
    ]

    project_keywords = [
        "project", "developed", "built", "created", "implemented",
        "designed", "developed", "internship", "experience",
        "worked", "engineered", "application", "system"
    ]

    matches = []
    seen = set()

    for line in lines:
        lower = line.lower()

        if any(keyword in lower for keyword in project_keywords):
            normalized = lower[:180]

            if normalized not in seen:
                matches.append(line[:300])
                seen.add(normalized)

    return matches[:8]


def calculate_role_skill_match(role, skills):
    role_skill_map = {
        "AI / ML Engineer": [
            "Python", "Machine Learning", "Deep Learning",
            "TensorFlow", "PyTorch", "Scikit-learn",
            "Computer Vision", "NLP", "CNN", "Transformers"
        ],
        "Data Scientist": [
            "Python", "Machine Learning", "Pandas", "NumPy",
            "Scikit-learn", "Data Science", "Data Analysis",
            "SQL", "Power BI", "Tableau"
        ],
        "Python Developer": [
            "Python", "SQL", "Git", "GitHub",
            "Flask", "Django", "Streamlit",
            "HTML", "CSS", "JavaScript"
        ],
        "Software Developer": [
            "Python", "Java", "C++", "SQL",
            "Git", "GitHub", "Docker",
            "HTML", "CSS", "JavaScript"
        ]
    }

    relevant = role_skill_map.get(role, [])
    detected_lower = {skill.lower() for skill in skills}

    matched = [
        skill for skill in relevant
        if skill.lower() in detected_lower
    ]

    percentage = (
        round((len(matched) / len(relevant)) * 100)
        if relevant else 0
    )

    return percentage, matched, relevant


def calculate_resume_readiness(
    resume_text,
    skills,
    projects,
    role_match
):
    score = 0

    if len(resume_text.strip()) >= 300:
        score += 20
    elif len(resume_text.strip()) >= 150:
        score += 12
    elif resume_text.strip():
        score += 6

    if len(skills) >= 8:
        score += 25
    elif len(skills) >= 5:
        score += 20
    elif len(skills) >= 3:
        score += 14
    elif skills:
        score += 8

    if len(projects) >= 3:
        score += 20
    elif len(projects) >= 1:
        score += 12

    score += round(role_match * 0.35)

    return min(score, 100)


def get_resume_suggestions(
    resume_text,
    skills,
    projects,
    role_match,
    role
):
    suggestions = []

    if not resume_text.strip():
        suggestions.append(
            "Upload a text-based PDF resume so it can be analyzed."
        )

    if len(skills) < 5:
        suggestions.append(
            "Make your technical skills section clearer and include "
            "relevant tools you have genuinely used."
        )

    if len(projects) < 2:
        suggestions.append(
            "Add more project details, including your role, technologies "
            "used, and the result or impact."
        )

    if role_match < 50:
        suggestions.append(
            f"Highlight skills and projects that are relevant to the "
            f"{role} position."
        )

    if len(resume_text.split()) < 150:
        suggestions.append(
            "Add concise details about education, experience, projects, "
            "and measurable achievements."
        )

    if not suggestions:
        suggestions.append(
            "Your resume has a solid foundation. Keep project descriptions "
            "specific and quantify results wherever possible."
        )

    return suggestions[:5]


def analyze_resume(resume_text, skills, role):
    summary = get_resume_summary(resume_text)
    projects = extract_resume_projects_experience(resume_text)

    role_match, matched_skills, relevant_skills = (
        calculate_role_skill_match(role, skills)
    )

    readiness = calculate_resume_readiness(
        resume_text,
        skills,
        projects,
        role_match
    )

    suggestions = get_resume_suggestions(
        resume_text,
        skills,
        projects,
        role_match,
        role
    )

    return {
        "summary": summary,
        "projects": projects,
        "role_match": role_match,
        "matched_skills": matched_skills,
        "relevant_skills": relevant_skills,
        "readiness": readiness,
        "suggestions": suggestions,
    }


# =========================================================
# ANSWER EVALUATION
# =========================================================

def evaluate_answer(answer, question, role):

    answer_lower = answer.lower().strip()
    words = answer_lower.split()
    word_count = len(words)

    technical_terms = [
        "python", "java", "c++", "sql", "machine learning",
        "deep learning", "model", "dataset", "data", "algorithm",
        "accuracy", "precision", "recall", "classification",
        "regression", "tensorflow", "pytorch", "keras", "opencv",
        "nlp", "cnn", "rnn", "lstm", "transformer", "api",
        "testing", "debugging", "deployment", "git", "github",
        "docker", "cloud", "aws", "azure", "streamlit", "flask",
        "django", "pandas", "numpy", "scikit-learn"
    ]

    practical_terms = [
        "implemented", "developed", "built", "created", "designed",
        "tested", "debugged", "deployed", "optimized", "improved",
        "solved", "project", "application", "system", "database",
        "training", "validation", "testing", "production", "result",
        "performance", "challenge", "solution", "approach"
    ]

    communication_terms = [
        "first", "then", "because", "therefore", "however",
        "for example", "finally", "overall", "also", "while"
    ]

    # Technical Knowledge: rewards relevant technical vocabulary
    technical_matches = [
        term for term in technical_terms
        if term in answer_lower
    ]

    if len(technical_matches) >= 5:
        technical = 10
    elif len(technical_matches) >= 3:
        technical = 8
    elif len(technical_matches) >= 1:
        technical = 6
    else:
        technical = 4

    # Relevance: compare important words in the question with the answer.
    question_words = {
        word.strip(".,!?():;\"'")
        for word in question.lower().split()
        if len(word.strip(".,!?():;\"'")) > 3
    }

    stop_words = {
        "tell", "about", "your", "what", "which", "would", "could",
        "have", "from", "with", "this", "that", "they", "them",
        "explain", "describe", "difference", "between", "does",
        "experience", "project", "worked", "work", "role", "person"
    }

    question_keywords = question_words - stop_words
    relevance_matches = sum(
        1 for word in question_keywords if word in answer_lower
    )

    if relevance_matches >= 3:
        relevance = 9
    elif relevance_matches >= 2:
        relevance = 8
    elif relevance_matches >= 1:
        relevance = 7
    else:
        relevance = 5

    # Clarity & Communication: rewards a sufficiently developed answer
    # with multiple connected ideas rather than only a short statement.
    communication_matches = sum(
        1 for term in communication_terms if term in answer_lower
    )

    sentence_count = max(
        1,
        len([part for part in answer.replace("!", ".").replace("?", ".").split(".") if part.strip()])
    )

    if word_count >= 80 and sentence_count >= 3 and communication_matches >= 1:
        clarity = 9
    elif word_count >= 50 and sentence_count >= 2:
        clarity = 8
    elif word_count >= 30:
        clarity = 7
    elif word_count >= 15:
        clarity = 6
    else:
        clarity = 4

    # Practical Understanding: looks for evidence of doing, solving,
    # testing, improving or applying something.
    practical_matches = sum(
        1 for term in practical_terms if term in answer_lower
    )

    if practical_matches >= 4:
        practical = 9
    elif practical_matches >= 2:
        practical = 8
    elif practical_matches >= 1:
        practical = 6
    else:
        practical = 4

    # Overall answer strength. Technical questions get a little more
    # weight on technical knowledge; general questions balance all areas.
    if any(term in question.lower() for term in [
        "machine learning", "python", "sql", "model", "classification",
        "regression", "algorithm", "git", "debugging", "technical"
    ]):
        score = round(
            technical * 0.35
            + relevance * 0.25
            + clarity * 0.20
            + practical * 0.20
        )
    else:
        score = round(
            technical * 0.20
            + relevance * 0.30
            + clarity * 0.25
            + practical * 0.25
        )

    score = max(1, min(score, 10))

    strengths = []
    improvements = []

    if technical >= 8:
        strengths.append("good technical detail")
    else:
        improvements.append("include more relevant technical concepts")

    if relevance >= 8:
        strengths.append("stayed relevant to the question")
    else:
        improvements.append("answer the question more directly")

    if clarity >= 8:
        strengths.append("clear and well-developed explanation")
    else:
        improvements.append("organize the answer into clearer points")

    if practical >= 8:
        strengths.append("showed practical understanding")
    else:
        improvements.append("add a real example, implementation step, or result")

    if score >= 9:
        level = "Excellent"
    elif score >= 7:
        level = "Good"
    elif score >= 5:
        level = "Developing"
    else:
        level = "Needs Improvement"

    if strengths:
        feedback = "Strong points: " + ", ".join(strengths) + ". "
    else:
        feedback = ""

    if improvements:
        feedback += "To improve: " + ", ".join(improvements) + "."
    else:
        feedback += "Keep this level of detail and support your points with specific examples."

    evaluation = {
        "technical": technical,
        "relevance": relevance,
        "clarity": clarity,
        "practical": practical,
        "level": level,
        "feedback": feedback,
        "technical_matches": technical_matches,
        "word_count": word_count
    }

    return score, feedback, evaluation


# =========================================================
# FINAL REPORT INSIGHTS
# =========================================================

def get_performance_level(score):
    if score >= 8.5:
        return "Excellent"
    elif score >= 7:
        return "Good"
    elif score >= 5:
        return "Fair"
    return "Needs Improvement"


def build_candidate_insights(evaluations, scores):
    if not evaluations:
        return {
            "strengths": ["Complete more interview answers to generate insights."],
            "improvements": ["Continue practicing clear, structured answers."],
            "topics": ["Interview communication", "Technical fundamentals"],
        }

    technical_avg = sum(e["technical"] for e in evaluations) / len(evaluations)
    relevance_avg = sum(e["relevance"] for e in evaluations) / len(evaluations)
    clarity_avg = sum(e["clarity"] for e in evaluations) / len(evaluations)
    practical_avg = sum(e["practical"] for e in evaluations) / len(evaluations)

    strengths = []
    improvements = []
    topics = []

    dimensions = [
        ("Technical Knowledge", technical_avg, "technical fundamentals"),
        ("Relevance", relevance_avg, "answer structure and question focus"),
        ("Clarity & Communication", clarity_avg, "clear communication"),
        ("Practical Understanding", practical_avg, "real-world problem solving"),
    ]

    for name, value, topic in dimensions:
        if value >= 8:
            strengths.append(f"Strong {name.lower()}.")
        elif value < 7:
            improvements.append(f"Improve {name.lower()}.")
            topics.append(topic)

    if not strengths:
        strengths.append("You completed the interview and showed willingness to explain your answers.")

    if not improvements:
        improvements.append("Keep adding specific examples, decisions, and measurable results.")

    if not topics:
        topics.extend([
            "Technical fundamentals",
            "Project-based explanations",
            "Interview communication",
        ])

    return {
        "strengths": strengths[:4],
        "improvements": improvements[:4],
        "topics": list(dict.fromkeys(topics))[:5],
    }


def calculate_average_time(question_times):
    if not question_times:
        return 0

    return sum(question_times) / len(question_times)


# =========================================================
# RESET
# =========================================================

def reset_interview():

    st.session_state.started = False
    st.session_state.finished = False

    st.session_state.candidate_name = ""
    st.session_state.role = ""
    st.session_state.resume_text = ""
    st.session_state.skills = []
    st.session_state.resume_analysis = {}

    st.session_state.questions = []
    st.session_state.current_question = 0

    st.session_state.answers = []
    st.session_state.scores = []
    st.session_state.feedback = []
    st.session_state.evaluations = []
    st.session_state.question_started_at = None
    st.session_state.question_times = []

    st.session_state.celebrated = False


# =========================================================
# PARTY CONFETTI BLAST
# =========================================================

def confetti_blast():

    components.html(
        """
        <!DOCTYPE html>

        <html>

        <head>

        <style>

        html,
        body {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: transparent;
        }

        .confetti {
            position: fixed;
            top: -30px;
            width: 10px;
            height: 18px;
            border-radius: 2px;
            z-index: 999999;

            animation-name: fall;
            animation-timing-function: ease-in;
            animation-fill-mode: forwards;
        }

        @keyframes fall {

            0% {
                top: -30px;
                opacity: 1;
                transform:
                    translateX(0)
                    rotate(0deg);
            }

            25% {
                transform:
                    translateX(35px)
                    rotate(180deg);
            }

            50% {
                transform:
                    translateX(-35px)
                    rotate(360deg);
            }

            75% {
                transform:
                    translateX(45px)
                    rotate(540deg);
            }

            100% {
                top: 105vh;
                opacity: 0;
                transform:
                    translateX(-20px)
                    rotate(720deg);
            }

        }

        </style>

        </head>

        <body>

        <script>

        const colors = [
            "#ff2f86",
            "#8f5de7",
            "#ffd34e",
            "#62c9a8",
            "#5da9e9",
            "#ff8b5c",
            "#e85db5",
            "#ff5c5c",
            "#7cce5b"
        ];

        for (let i = 0; i < 180; i++) {

            const piece =
                document.createElement("div");

            piece.className = "confetti";

            piece.style.left =
                Math.random() * 100 + "vw";

            piece.style.backgroundColor =
                colors[
                    Math.floor(
                        Math.random() * colors.length
                    )
                ];

            piece.style.width =
                (6 + Math.random() * 8) + "px";

            piece.style.height =
                (9 + Math.random() * 12) + "px";

            piece.style.animationDuration =
                (2.5 + Math.random() * 2.5) + "s";

            piece.style.animationDelay =
                (Math.random() * 0.8) + "s";

            document.body.appendChild(piece);

        }

        </script>

        </body>

        </html>
        """,
        height=650
    )


# =========================================================
# LANDING PAGE
# =========================================================

if not st.session_state.started:

    st.markdown(
        """
        <div class="brand">
            AI <span>Interviewer</span>
        </div>

        <div class="subtitle">
            A smart and friendly way to practice your interview.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    # -----------------------------------------------------
    # HERO
    # -----------------------------------------------------

    with st.container(border=True):

        left, right = st.columns([1.5, 1])

        with left:

            st.markdown(
                """
                <div class="small-label">
                    SMART INTERVIEW PRACTICE
                </div>
                """,
                unsafe_allow_html=True
            )

            st.header(
                "Your next interview starts here."
            )

            st.write(
                "Upload your resume, choose your role, "
                "and answer interview questions designed "
                "around your career."
            )

            st.success(
                "Resume analysis • "
                "Interview practice • "
                "Performance report"
            )

        with right:

            st.image(
                "https://images.unsplash.com/photo-1556761175-b413da4baf72"
                "?auto=format&fit=crop&w=900&q=75",
                use_container_width=True
            )

    st.write("")

    # -----------------------------------------------------
    # FEATURES
    # -----------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        with st.container(border=True):

            st.markdown(
                '<div class="feature-title">'
                'Resume Analysis'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="feature-text">'
                'Upload your PDF resume and identify '
                'relevant skills.'
                '</div>',
                unsafe_allow_html=True
            )

    with col2:

        with st.container(border=True):

            st.markdown(
                '<div class="feature-title">'
                'Interview Practice'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="feature-text">'
                'Answer realistic questions in a '
                'conversation-style interview.'
                '</div>',
                unsafe_allow_html=True
            )

    with col3:

        with st.container(border=True):

            st.markdown(
                '<div class="feature-title">'
                'Performance Report'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="feature-text">'
                'Review your scores and feedback after '
                'the interview.'
                '</div>',
                unsafe_allow_html=True
            )

    st.write("")

    # -----------------------------------------------------
    # CANDIDATE SETUP
    # -----------------------------------------------------

    with st.container(border=True):

        st.subheader(
            "Let's get you ready"
        )

        name = st.text_input(
            "Candidate Name",
            placeholder="Enter your name"
        )

        role = st.selectbox(
            "Interview Role",
            [
                "AI / ML Engineer",
                "Data Scientist",
                "Python Developer",
                "Software Developer"
            ]
        )

        resume = st.file_uploader(
            "Upload your Resume",
            type=["pdf"]
        )

        st.write("")

        start_button = st.button(
            "Start My Interview",
            use_container_width=True
        )

        if start_button:

            if not name.strip():

                st.warning(
                    "Please enter your name before starting."
                )

            elif resume is None:

                st.warning(
                    "Please upload your PDF resume."
                )

            else:

                with st.spinner(
                    "Preparing your interview..."
                ):

                    resume_text = (
                        extract_text_from_resume(resume)
                    )

                    skills = extract_skills(
                        resume_text
                    )

                    resume_analysis = analyze_resume(
                        resume_text,
                        skills,
                        role
                    )

                    st.session_state.candidate_name = name
                    st.session_state.role = role
                    st.session_state.resume_text = resume_text
                    st.session_state.skills = skills
                    st.session_state.resume_analysis = resume_analysis

                    st.session_state.questions = (
                        ROLE_QUESTIONS[role]
                    )

                    st.session_state.current_question = 0
                    st.session_state.answers = []
                    st.session_state.scores = []
                    st.session_state.feedback = []
                    st.session_state.question_started_at = None
                    st.session_state.question_times = []

                    st.session_state.started = True
                    st.session_state.finished = False

                    time.sleep(0.5)

                st.rerun()


# =========================================================
# INTERVIEW PAGE
# =========================================================

elif (
    st.session_state.started
    and not st.session_state.finished
):

    left, right = st.columns([3, 1])

    with left:

        st.markdown(
            """
            <div class="brand">
                AI <span>Interviewer</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write(
            f"Welcome, "
            f"**{st.session_state.candidate_name}**."
        )

    with right:

        if st.button("Exit Interview"):

            reset_interview()
            st.rerun()

    st.write("")

    total_questions = len(
        st.session_state.questions
    )

    current = (
        st.session_state.current_question
    )

    # Start the timer only once for this question.
    # Streamlit reruns will not reset it.
    if st.session_state.question_started_at is None:
        st.session_state.question_started_at = time.time()

    elapsed_seconds = max(
        0,
        int(time.time() - st.session_state.question_started_at)
    )

    st.progress(
        current / total_questions
    )

    st.caption(
        f"Question {current + 1} of "
        f"{total_questions} • "
        f"{st.session_state.role}"
    )

    timer_col, tip_col = st.columns([1, 2])

    with timer_col:
        minutes = elapsed_seconds // 60
        seconds = elapsed_seconds % 60
        st.metric(
            "Time spent",
            f"{minutes:02d}:{seconds:02d}"
        )

    with tip_col:
        st.info(
            "Answer tip: explain your approach, give a "
            "specific example, and mention the result when possible."
        )

    st.write("")

    # -----------------------------------------------------
    # INTERVIEW BUDDY
    # -----------------------------------------------------

    if current == 0 and not st.session_state.answers:

        show_interview_buddy(
            "Hi! Take a breath, read the question carefully "
            "and answer naturally. You've got this!"
        )

    elif current == total_questions - 1:

        show_interview_buddy(
            "This is your final question. Give it your best "
            "answer and finish strong!",
            "happy"
        )

    else:

        show_interview_buddy(
            "Take your time. Try to include a specific "
            "example from your experience."
        )

    # -----------------------------------------------------
    # SKILLS
    # -----------------------------------------------------

    if st.session_state.skills:

        with st.expander(
            "Skills detected from your resume"
        ):

            st.write(
                ", ".join(
                    st.session_state.skills
                )
            )

    st.write("")

    # -----------------------------------------------------
    # RESUME ANALYSIS
    # -----------------------------------------------------

    analysis = st.session_state.resume_analysis

    if analysis:
        with st.expander("View Resume Analysis", expanded=False):
            st.subheader("Resume Summary")
            st.write(analysis["summary"])

            st.subheader("Role-Skill Match")
            st.progress(analysis["role_match"] / 100)
            st.caption(
                f"{analysis['role_match']}% match for "
                f"{st.session_state.role}"
            )

            if analysis["matched_skills"]:
                st.write(
                    "**Relevant skills found:** "
                    + ", ".join(analysis["matched_skills"])
                )
            else:
                st.write(
                    "No strongly matching role-specific skills were detected."
                )

            st.subheader("Projects & Experience Signals")
            if analysis["projects"]:
                for item in analysis["projects"]:
                    st.write(f"• {item}")
            else:
                st.write(
                    "No clear project or experience descriptions were detected."
                )

            st.subheader("Resume Readiness")
            st.progress(analysis["readiness"] / 100)
            st.caption(
                f"Resume readiness score: "
                f"{analysis['readiness']}/100"
            )

            st.subheader("Suggestions")
            for suggestion in analysis["suggestions"]:
                st.write(f"💡 {suggestion}")

    st.write("")

    # -----------------------------------------------------
    # PREVIOUS CONVERSATION
    # -----------------------------------------------------

    if st.session_state.answers:

        st.markdown(
            '<div class="conversation-title">'
            'Your Interview Conversation'
            '</div>',
            unsafe_allow_html=True
        )

        st.write("")

        for i, answer in enumerate(
            st.session_state.answers
        ):

            with st.chat_message("assistant"):

                st.write(
                    st.session_state.questions[i]
                )

            with st.chat_message("user"):

                st.write(answer)

                st.caption(
                    f"Answer score: "
                    f"{st.session_state.scores[i]}/10"
                )

        st.divider()

    # -----------------------------------------------------
    # CURRENT QUESTION
    # -----------------------------------------------------

    with st.container(border=True):

        st.markdown(
            '<div class="small-label">'
            'CURRENT QUESTION'
            '</div>',
            unsafe_allow_html=True
        )

        st.subheader(
            st.session_state.questions[current]
        )

        st.write(
            "Take your time and answer naturally. "
            "Try to include examples from your experience."
        )

        answer = st.text_area(
            "Your Answer",
            placeholder="Type your answer here...",
            height=180,
            key=f"answer_{current}"
        )

        word_count = len(answer.split())

        st.caption(
            f"Words: {word_count}"
        )

        # Answer guidance

        if 0 < word_count < 30:

            show_interview_buddy(
                "Your answer is a little short. "
                "Try adding what you did, why you chose that "
                "approach, and what the result was."
            )

        elif 30 <= word_count < 50:

            show_interview_buddy(
                "Good start! One specific example or result "
                "would make your answer stronger."
            )

        elif word_count >= 50:

            show_interview_buddy(
                "Nice! You're giving a detailed answer. "
                "Keep the explanation clear and focused.",
                "happy"
            )

        submit = st.button(
            "Submit Answer",
            use_container_width=True
        )

        if submit:

            if not answer.strip():

                st.warning(
                    "Please enter an answer before submitting."
                )

            else:

                score, feedback, evaluation = evaluate_answer(
                    answer,
                    st.session_state.questions[current],
                    st.session_state.role
                )

                time_taken = max(
                    0,
                    int(
                        time.time()
                        - st.session_state.question_started_at
                    )
                )

                st.session_state.answers.append(
                    answer
                )

                st.session_state.scores.append(
                    score
                )

                st.session_state.feedback.append(
                    feedback
                )

                st.session_state.evaluations.append(
                    evaluation
                )

                st.session_state.question_times.append(
                    time_taken
                )

                st.session_state.current_question += 1
                st.session_state.question_started_at = None

                if (
                    st.session_state.current_question
                    >= total_questions
                ):

                    st.session_state.finished = True

                st.rerun()


# =========================================================
# FINAL REPORT
# =========================================================

else:

    # -----------------------------------------------------
    # BALLOONS
    # -----------------------------------------------------

    if not st.session_state.celebrated:

        st.balloons()

        st.session_state.celebrated = True

    st.markdown(
        """
        <div class="brand">
            AI <span>Interviewer</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    # -----------------------------------------------------
    # FINAL BUDDY
    # -----------------------------------------------------

    show_interview_buddy(
        "You did it! Your interview is complete. "
        "Take a moment to celebrate your progress!",
        "celebrate"
    )

    # -----------------------------------------------------
    # COMPLETION CARD
    # -----------------------------------------------------

    with st.container(border=True):

        st.markdown(
            """
            <div class="small-label">
                INTERVIEW COMPLETED
            </div>
            """,
            unsafe_allow_html=True
        )

        st.title(
            f"Great job, "
            f"{st.session_state.candidate_name}!"
        )

        st.write(
            "You have successfully completed your interview."
        )

        st.write("")

        if st.session_state.scores:

            average_score = (
                sum(st.session_state.scores)
                / len(st.session_state.scores)
            )

        else:

            average_score = 0

        score_col, info_col = st.columns([1, 2])

        with score_col:

            st.markdown(
                f"""
                <p class="score-number">
                    {average_score:.1f}
                </p>

                <p class="score-caption">
                    Overall Score / 10
                </p>
                """,
                unsafe_allow_html=True
            )

        with info_col:

            if average_score >= 8.5:

                st.success(
                    "Excellent performance! "
                    "Your answers showed strong "
                    "communication and technical understanding."
                )

            elif average_score >= 7:

                st.info(
                    "Good performance! "
                    "With more detail and stronger examples, "
                    "your answers can become even better."
                )

            else:

                st.warning(
                    "Keep practicing! Focus on clearer "
                    "and more detailed answers."
                )

    st.write("")

    # -----------------------------------------------------
    # CANDIDATE INSIGHTS
    # -----------------------------------------------------

    insights = build_candidate_insights(
        st.session_state.evaluations,
        st.session_state.scores
    )

    performance_level = get_performance_level(
        average_score
    )

    average_time = calculate_average_time(
        st.session_state.question_times
    )

    avg_minutes = int(average_time) // 60
    avg_seconds = int(average_time) % 60

    with st.container(border=True):
        st.subheader("Candidate Insights")

        insight_col1, insight_col2, insight_col3 = st.columns(3)

        with insight_col1:
            st.markdown("**Performance Level**")
            st.success(performance_level)

        with insight_col2:
            st.markdown("**Average Answer Time**")
            st.info(
                f"{avg_minutes:02d}:{avg_seconds:02d}"
            )

        with insight_col3:
            st.markdown("**Questions Completed**")
            st.info(
                f"{len(st.session_state.answers)} / "
                f"{len(st.session_state.questions)}"
            )

        st.write("")

        strength_col, improve_col = st.columns(2)

        with strength_col:
            st.markdown("### Strengths")
            for item in insights["strengths"]:
                st.write(f"• {item}")

        with improve_col:
            st.markdown("### Areas to Improve")
            for item in insights["improvements"]:
                st.write(f"• {item}")

        st.write("")

        st.markdown("### Recommended Practice Topics")
        st.write(
            " • ".join(insights["topics"])
        )

    st.write("")

    # -----------------------------------------------------
    # SCORE BREAKDOWN
    # -----------------------------------------------------

    with st.container(border=True):

        st.subheader(
            "Interview Score Breakdown"
        )

        for i, score in enumerate(
            st.session_state.scores
        ):

            st.write(
                f"Question {i + 1}: {st.session_state.questions[i]}"
            )

            st.progress(
                score / 10
            )

            st.caption(
                f"Overall Answer Score: {score}/10"
            )

            if i < len(st.session_state.evaluations):
                evaluation = st.session_state.evaluations[i]

                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

                with metric_col1:
                    st.metric("Technical", f"{evaluation['technical']}/10")

                with metric_col2:
                    st.metric("Relevance", f"{evaluation['relevance']}/10")

                with metric_col3:
                    st.metric("Clarity", f"{evaluation['clarity']}/10")

                with metric_col4:
                    st.metric("Practical", f"{evaluation['practical']}/10")

                if i < len(st.session_state.question_times):
                    total_seconds = st.session_state.question_times[i]
                    time_minutes = total_seconds // 60
                    time_seconds = total_seconds % 60
                    time_text = f"{time_minutes:02d}:{time_seconds:02d}"
                else:
                    time_text = "N/A"

                st.caption(
                    f"Performance Level: {evaluation['level']} • "
                    f"Answer length: {evaluation['word_count']} words • "
                    f"Time taken: {time_text}"
                )

            st.write(
                st.session_state.feedback[i]
            )

            if i < len(
                st.session_state.scores
            ) - 1:

                st.divider()

    st.write("")

    # -----------------------------------------------------
    # COMPLETE CONVERSATION
    # -----------------------------------------------------

    with st.expander(
        "View Complete Interview Conversation"
    ):

        for i, answer in enumerate(
            st.session_state.answers
        ):

            st.markdown(
                f"**Question {i + 1}:** "
                f"{st.session_state.questions[i]}"
            )

            st.markdown(
                f"**Candidate:** {answer}"
            )

            st.markdown(
                f"**Score:** "
                f"{st.session_state.scores[i]}/10"
            )

            if i < len(st.session_state.evaluations):
                evaluation = st.session_state.evaluations[i]
                st.caption(
                    f"Technical: {evaluation['technical']}/10 • "
                    f"Relevance: {evaluation['relevance']}/10 • "
                    f"Clarity: {evaluation['clarity']}/10 • "
                    f"Practical: {evaluation['practical']}/10"
                )

            if i < len(st.session_state.question_times):
                total_seconds = st.session_state.question_times[i]
                time_minutes = total_seconds // 60
                time_seconds = total_seconds % 60
                st.caption(
                    f"Time taken: {time_minutes:02d}:{time_seconds:02d}"
                )

            st.divider()

    st.write("")

    # -----------------------------------------------------
    # RESUME SKILLS
    # -----------------------------------------------------

    if st.session_state.skills:

        with st.container(border=True):

            st.subheader(
                "Skills Found in Your Resume"
            )

            st.write(
                ", ".join(
                    st.session_state.skills
                )
            )

    st.write("")
    st.write("")

    # =====================================================
    # PARTY TIME
    # =====================================================

    st.balloons()

    confetti_blast()

    st.write("")

    st.success(
        "Interview completed successfully!"
    )

    st.write("")

    if st.button(
        "Start a New Interview",
        use_container_width=True
    ):

        reset_interview()
        st.rerun()