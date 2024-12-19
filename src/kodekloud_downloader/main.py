import logging
import re
import requests
from pathlib import Path
from typing import Union, List
import concurrent.futures
from collections import defaultdict
from kodekloud_downloader.helpers import (
    download_all_pdf, download_video, is_normal_content, normalize_name, parse_token
)
from kodekloud_downloader.models.course import CourseDetail
from kodekloud_downloader.models.courses import Course
from kodekloud_downloader.models.helper import fetch_course_detail
from kodekloud_downloader.models.quiz import Quiz

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def sanitize_filename(filename: str) -> str:
    """Sanitize the filename to remove invalid characters."""
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    sanitized = sanitized.strip()  # Remove leading/trailing spaces
    return sanitized

def download_quiz(output_dir: str, sep: bool) -> None:
    """
    Download quizzes from the API and save them as Markdown files.
    :param output_dir: The directory path where the Markdown files will be saved.
    :param sep: If True, each quiz will be saved as a separate file. If False, all quizzes are combined into one file.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    quiz_markdown = [] if sep else ["# KodeKloud Quiz"]

    try:
        response = requests.get("https://mcq-backend-main.kodekloud.com/api/quizzes/all")
        response.raise_for_status()  # Will raise an exception for non-2xx responses
        quizzes = [Quiz(**item) for item in response.json()]
        logger.info(f"Total {len(quizzes)} quizzes available!")

        for quiz_index, quiz in enumerate(quizzes, start=1):
            quiz_name = quiz.name or quiz.topic
            sanitized_quiz_name = sanitize_filename(quiz_name)
            quiz_markdown.append(f"\n## {quiz_name}")
            logger.info(f"Fetching Quiz {quiz_index} - {quiz_name}")
            questions = quiz.fetch_questions()

            for index, question in enumerate(questions, start=1):
                quiz_markdown.append(f"\n**{index}. {question.question.strip()}**")
                quiz_markdown.append("\n")
                for answer in question.answers:
                    quiz_markdown.append(f"* [ ] {answer}")
                quiz_markdown.append(f"\n**Correct answer:**")
                for answer in question.correctAnswers:
                    quiz_markdown.append(f"* [x] {answer}")

                if script := question.code.get("script"):
                    quiz_markdown.append(f"\n**Code**: \n{script}")
                if question.explanation:
                    quiz_markdown.append(f"\n**Explanation**: {question.explanation}")
                if question.documentationLink:
                    quiz_markdown.append(f"\n**Documentation Link**: {question.documentationLink}")

            # Writing to separate file if `sep` is True
            if sep:
                output_file = output_dir / f"{sanitized_quiz_name}.md"
                markdown_text = "\n".join(quiz_markdown)
                try:
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(markdown_text)
                    logger.info(f"Quiz file written to {output_file}")
                except IOError as e:
                    logger.error(f"Error writing file {output_file}: {e}")
                quiz_markdown = []
            else:
                quiz_markdown.append("\n---\n")

        # Writing all quizzes to a single file if `sep` is False
        if not sep:
            output_file = output_dir / "KodeKloud_Quiz.md"
            markdown_text = "\n".join(quiz_markdown)
            try:
                Path(output_file).write_text(markdown_text, encoding="utf-8")
                logger.info(f"Quiz file written to {output_file}")
            except IOError as e:
                logger.error(f"Error writing file {output_file}: {e}")

    except requests.RequestException as e:
        logger.error(f"Error fetching quiz data: {e}")
