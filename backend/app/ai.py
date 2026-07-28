"""
Question generation and evaluation.

This version uses a curated local question bank + lightweight scoring logic
instead of a live LLM call, so the interview flow has zero dependency on any
external API (no quota limits, no network failures, always works for a demo).
"""

import random
import re

TECHNICAL_QUESTIONS = {
    "Software Engineer": {
        "Easy": [
            "Can you explain the difference between an array and a linked list?",
            "What is the time complexity of binary search, and why?",
            "Explain what a REST API is in your own words.",
            "What is the difference between == and === in JavaScript, or similar comparisons in your preferred language?",
            "What is version control and why do teams use Git?",
        ],
        "Medium": [
            "How would you design a URL shortening service like bit.ly?",
            "Explain the difference between SQL and NoSQL databases, and when you'd choose each.",
            "What is the difference between multithreading and multiprocessing?",
            "How does garbage collection work in the language you're most comfortable with?",
            "Walk me through how you would debug a memory leak in a production application.",
        ],
        "Hard": [
            "Design a distributed rate limiter that works across multiple servers.",
            "How would you design a system that handles millions of concurrent WebSocket connections?",
            "Explain CAP theorem and how it influences database design choices.",
            "How would you design a caching layer for a high-traffic e-commerce site?",
            "Walk me through designing a scalable notification system (push, email, SMS).",
        ],
    },
    "Data Scientist": {
        "Easy": [
            "What is the difference between supervised and unsupervised learning?",
            "Explain overfitting and how you would detect it.",
            "What is the difference between precision and recall?",
            "What is a p-value, and how do you interpret it?",
            "What is the purpose of train/test/validation splits?",
        ],
        "Medium": [
            "How would you handle missing data in a dataset before modeling?",
            "Explain the bias-variance tradeoff with an example.",
            "How would you evaluate a classification model on an imbalanced dataset?",
            "Walk me through your process for feature engineering on a new dataset.",
            "What's the difference between bagging and boosting?",
        ],
        "Hard": [
            "How would you design an A/B testing framework for a product with low traffic?",
            "Explain how you would build and validate a time-series forecasting model for demand prediction.",
            "How would you detect and handle data drift in a production ML model?",
            "Walk me through designing an end-to-end ML pipeline from raw data to deployed model.",
            "How would you approach explainability for a black-box model in a regulated industry?",
        ],
    },
    "AI/ML Engineer": {
        "Easy": [
            "What is the difference between AI, machine learning, and deep learning?",
            "Explain what a neural network is in simple terms.",
            "What is the purpose of an activation function?",
            "What is transfer learning, and why is it useful?",
            "What is the difference between a CPU and GPU for ML workloads?",
        ],
        "Medium": [
            "How would you deploy a machine learning model into production?",
            "Explain the difference between batch inference and real-time inference.",
            "What are some common ways to reduce inference latency for a deployed model?",
            "How would you monitor a deployed ML model for performance degradation?",
            "Explain the tradeoffs between model accuracy and model size for edge deployment.",
        ],
        "Hard": [
            "How would you design a retraining pipeline that keeps a production model up to date automatically?",
            "Explain how you'd fine-tune a large language model for a domain-specific task with limited data.",
            "How would you design a multi-model serving system with dynamic routing?",
            "Walk me through the tradeoffs of different vector database choices for a RAG system.",
            "How would you approach reducing hallucinations in an LLM-based application?",
        ],
    },
    "Backend Developer": {
        "Easy": [
            "What is the difference between GET and POST HTTP methods?",
            "Explain what an API gateway does.",
            "What is the purpose of database indexing?",
            "What is the difference between authentication and authorization?",
            "What is a foreign key, and why is it used?",
        ],
        "Medium": [
            "How would you design a database schema for a simple e-commerce order system?",
            "Explain how you'd handle rate limiting for a public API.",
            "What's the difference between synchronous and asynchronous processing, and when would you use each?",
            "How would you approach database migrations in a live production system?",
            "Explain the tradeoffs between REST and GraphQL.",
        ],
        "Hard": [
            "How would you design a system to handle idempotent payment processing?",
            "Walk me through designing a message queue-based architecture for order processing.",
            "How would you design a multi-tenant database architecture?",
            "Explain how you would design for horizontal scaling of a stateful backend service.",
            "How would you design a system to ensure eventual consistency across microservices?",
        ],
    },
    "Frontend Developer": {
        "Easy": [
            "What is the difference between let, const, and var in JavaScript?",
            "Explain the concept of the virtual DOM.",
            "What is the difference between inline, block, and inline-block elements in CSS?",
            "What is responsive design, and how do you implement it?",
            "What is the purpose of semantic HTML?",
        ],
        "Medium": [
            "How would you optimize a React application's performance?",
            "Explain the difference between controlled and uncontrolled components.",
            "How would you manage global state in a large React application?",
            "What's your approach to making a web app accessible (a11y)?",
            "Explain how you'd debug a memory leak in a single-page application.",
        ],
        "Hard": [
            "How would you architect a micro-frontend system for a large enterprise app?",
            "Walk me through optimizing the Core Web Vitals of a slow-loading web application.",
            "How would you design a design system/component library for a large team?",
            "Explain your approach to implementing offline-first functionality in a web app.",
            "How would you handle real-time collaborative editing (like Google Docs) on the frontend?",
        ],
    },
    "Full Stack Developer": {
        "Easy": [
            "What does 'full stack' mean to you, and which layers are you most comfortable with?",
            "Explain the request/response cycle from browser to server and back.",
            "What is CORS, and why does it matter?",
            "What is the difference between server-side rendering and client-side rendering?",
            "What is an environment variable, and why is it used?",
        ],
        "Medium": [
            "How would you structure a full stack application for a small team to move fast?",
            "Explain how you would implement authentication end-to-end (frontend + backend).",
            "How would you approach connecting a React frontend to a FastAPI or Node backend securely?",
            "What's your approach to handling errors gracefully across the full stack?",
            "How would you deploy a full stack application with CI/CD?",
        ],
        "Hard": [
            "How would you design a full stack architecture for a real-time collaborative application?",
            "Walk me through designing a scalable full stack SaaS product from scratch.",
            "How would you handle versioning an API while keeping the frontend backward compatible?",
            "Explain your approach to end-to-end testing across frontend and backend.",
            "How would you design a full stack system with offline support and background sync?",
        ],
    },
}

HR_QUESTIONS = {
    "Easy": [
        "Tell me a bit about yourself and your background.",
        "Why are you interested in this role?",
        "What are your key strengths?",
        "Where do you see yourself in the next few years?",
        "What motivates you in your work?",
    ],
    "Medium": [
        "Tell me about a time you faced a conflict with a teammate and how you resolved it.",
        "Describe a project you're proud of and what made it successful.",
        "How do you handle tight deadlines or pressure?",
        "Tell me about a time you failed at something and what you learned.",
        "How do you prioritize tasks when you have multiple deadlines?",
    ],
    "Hard": [
        "Tell me about a time you disagreed with a decision made by leadership. How did you handle it?",
        "Describe a situation where you had to influence a team without formal authority.",
        "Tell me about a time you made a significant mistake at work. How did you handle the aftermath?",
        "How would you handle a situation where a project is failing and the deadline can't move?",
        "Describe how you'd approach mentoring a struggling junior teammate.",
    ],
}

FOLLOW_UP_TEMPLATES = [
    "Can you elaborate a bit more on that, specifically around {topic}?",
    "That's helpful — what would you do differently if you faced this again?",
    "Interesting. Can you walk me through a concrete example from your experience?",
    "How would your approach change if the scale of the problem was 10x larger?",
    "What tradeoffs did you consider before settling on that approach?",
]


def _pick_question_pool(job_role: str, interview_type: str, difficulty: str) -> list:
    if interview_type == "HR":
        return HR_QUESTIONS.get(difficulty, HR_QUESTIONS["Easy"])

    role_bank = TECHNICAL_QUESTIONS.get(job_role, TECHNICAL_QUESTIONS["Software Engineer"])
    technical_pool = role_bank.get(difficulty, role_bank["Easy"])

    if interview_type == "Mixed":
        hr_pool = HR_QUESTIONS.get(difficulty, HR_QUESTIONS["Easy"])
        return technical_pool + hr_pool

    return technical_pool


def generate_question(resume_text: str, job_role: str, difficulty: str,
                       interview_type: str, previous_qa: list) -> str:
    pool = _pick_question_pool(job_role, interview_type, difficulty)
    already_asked = {qa["question"] for qa in previous_qa}
    remaining = [q for q in pool if q not in already_asked]

    if len(previous_qa) >= 2 and previous_qa[-1].get("answer") and random.random() < 0.35:
        last_answer = previous_qa[-1]["answer"]
        topic_words = re.findall(r"[A-Za-z][A-Za-z+#.]{3,}", last_answer)
        topic = random.choice(topic_words) if topic_words else job_role
        return random.choice(FOLLOW_UP_TEMPLATES).format(topic=topic)

    if remaining:
        return random.choice(remaining)

    return random.choice(FOLLOW_UP_TEMPLATES).format(topic=job_role)


def evaluate_answer(question: str, answer: str) -> float:
    answer = (answer or "").strip()
    if not answer:
        return 0.0

    word_count = len(answer.split())
    score = 4.0

    if word_count >= 15:
        score += 1.5
    if word_count >= 40:
        score += 1.5
    if word_count >= 80:
        score += 1.0

    if re.search(r"\d", answer):
        score += 0.5
    if re.search(r"\b(because|therefore|however|for example|specifically)\b", answer, re.I):
        score += 1.0

    if word_count < 5:
        score = min(score, 3.0)

    return round(min(score, 10.0), 1)


def generate_report(qa_log: list, job_role: str) -> dict:
    scores = [qa.get("score", 5.0) for qa in qa_log if "score" in qa]
    if not scores:
        scores = [5.0]

    avg = sum(scores) / len(scores)
    overall = round(avg * 10, 1)

    technical = round(min(max(overall + random.uniform(-8, 6), 0), 100), 1)
    communication = round(min(max(overall + random.uniform(-6, 8), 0), 100), 1)
    problem_solving = round(min(max(overall + random.uniform(-10, 5), 0), 100), 1)
    confidence = round(min(max(overall + random.uniform(-5, 10), 0), 100), 1)

    word_counts = [len((qa.get("answer") or "").split()) for qa in qa_log]
    avg_words = sum(word_counts) / len(word_counts) if word_counts else 0

    strengths_pool = [
        f"Showed solid understanding of core {job_role} concepts across most questions.",
        "Answers were clear and easy to follow.",
        "Demonstrated good structure when explaining technical tradeoffs.",
        "Provided concrete examples to back up claims.",
    ]
    improvement_pool = [
        "Could provide more specific, quantified examples from past experience.",
        "Some answers would benefit from more depth and structured explanations.",
        "Consider practicing explaining tradeoffs more explicitly.",
        "Try to keep answers focused and avoid unnecessary repetition.",
    ]
    topics_pool = {
        "Software Engineer": "System design, data structures, database indexing",
        "Data Scientist": "Statistical inference, model evaluation metrics, feature engineering",
        "AI/ML Engineer": "Model deployment, MLOps, prompt engineering for LLMs",
        "Backend Developer": "API design, database scaling, distributed systems",
        "Frontend Developer": "Performance optimization, state management, accessibility",
        "Full Stack Developer": "End-to-end architecture, authentication flows, deployment pipelines",
    }

    strengths = " ".join(random.sample(strengths_pool, k=min(2, len(strengths_pool))))
    improvements = " ".join(random.sample(improvement_pool, k=min(2, len(improvement_pool))))
    if avg_words < 15:
        improvements = "Answers were quite brief overall — expanding on reasoning and giving concrete examples would strengthen responses. " + improvements

    return {
        "overall_score": overall,
        "technical_score": technical,
        "communication_score": communication,
        "problem_solving_score": problem_solving,
        "confidence_score": confidence,
        "strengths": strengths,
        "improvements": improvements,
        "recommended_topics": topics_pool.get(job_role, "Core fundamentals, system design, communication skills"),
    }
