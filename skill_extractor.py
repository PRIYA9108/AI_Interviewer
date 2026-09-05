def extract_skills(resume_text):

    skills_database = [
        "Python",
        "Java",
        "C++",
        "SQL",
        "Machine Learning",
        "Deep Learning",
        "TensorFlow",
        "PyTorch",
        "Keras",
        "Scikit-learn",
        "Pandas",
        "NumPy",
        "OpenCV",
        "NLP",
        "Natural Language Processing",
        "Computer Vision",
        "CNN",
        "RNN",
        "LSTM",
        "Transformers",
        "Streamlit",
        "Flask",
        "Django",
        "React",
        "HTML",
        "CSS",
        "JavaScript",
        "Git",
        "GitHub",
        "Docker",
        "AWS",
        "Azure",
        "Power BI",
        "Tableau",
        "Data Science",
        "Data Analysis"
    ]

    resume_text_lower = resume_text.lower()

    detected_skills = []

    for skill in skills_database:

        if skill.lower() in resume_text_lower:
            detected_skills.append(skill)

    return detected_skills
