import concurrent.futures
import queue
from dataclasses import dataclass
from typing import Dict, List, Optional
import requests


@dataclass
class QuizQuestion:
    _id: Dict[str, str]
    type: int
    correctAnswers: List[str]
    code: Dict[str, str]
    question: str
    answers: List[str]
    labels: Optional[List[str]] = None
    documentationLink: Optional[str] = None
    explanation: Optional[str] = None
    topic: Optional[str] = None


@dataclass
class Quiz:
    _id: Dict[str, str]
    questions: Dict[str, str]
    name: Optional[str] = None
    topic: Optional[str] = None
    projectId: Optional[str] = None
    order: Optional[str] = None

    def fetch_questions(self) -> List[QuizQuestion]:
        # Create a thread-safe queue to collect results
        quiz_questions_queue = queue.Queue()

        def fetch_question(question_id: str):
            params = {
                "id": question_id,
            }
            url = "https://mcq-backend-main.kodekloud.com/api/questions/question"
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()  # Will raise an exception for HTTP errors
                if question_json := response.json():
                    # Add the result to the queue in a thread-safe manner
                    quiz_questions_queue.put(QuizQuestion(**question_json))
            except requests.RequestException as e:
                print(f"Error fetching question {question_id}: {e}")

        # Use ThreadPoolExecutor to fetch questions concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Map the fetch_question function to the question IDs
            executor.map(fetch_question, self.questions.values())

        # Collect the results from the queue
        quiz_questions = []
        while not quiz_questions_queue.empty():
            quiz_questions.append(quiz_questions_queue.get())

        return quiz_questions
