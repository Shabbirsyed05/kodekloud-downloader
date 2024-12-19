import logging
from pathlib import Path
from typing import Union

import click
import validators

from kodekloud_downloader.enums import Quality
from kodekloud_downloader.helpers import select_courses
from kodekloud_downloader.main import (
    download_course,
    download_quiz,
    parse_course_from_url,
)
from kodekloud_downloader.models.helper import collect_all_courses


@click.group()
@click.option("-v", "--verbose", count=True, help="Increase log level verbosity")
def kodekloud(verbose):
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    if verbose == 1:
        logging.getLogger().setLevel(logging.INFO)
    elif verbose >= 2:
        logging.getLogger().setLevel(logging.DEBUG)


@kodekloud.command()
@click.argument("course_url", required=False)
@click.option(
    "--quality",
    "-q",
    default="1080p",
    type=click.Choice([quality.value for quality in Quality]),
    help="Quality of the video to be downloaded.",
)
@click.option(
    "--output-dir",
    "-o",
    default=Path.home() / "Downloads",
    help="Output directory where downloaded files will be store.",
)
@click.option(
    "--cookie",
    "-c",
    required=True,
    help="Cookie file. Course should be accessible via this.",
)
@click.option(
    "--max-duplicate-count",
    "-mdc",
    default=3,
    type=int,
    help="If same video is downloaded this many times, then download stops",
)
def dl(
    course_url,
    quality: str,
    output_dir: Union[Path, str],
    cookie,
    max_duplicate_count: int,
):
    if course_url is None:
        courses = collect_all_courses()
        selected_courses = select_courses(courses)
        for selected_course in selected_courses:
            download_course(
                course=selected_course,
                cookie=cookie,
                quality=quality,
                output_dir=output_dir,
                max_duplicate_count=max_duplicate_count,
            )
    elif validators.url(course_url):
        course_detail = parse_course_from_url(course_url)
        download_course(
            course=course_detail,
            cookie=cookie,
            quality=quality,
            output_dir=output_dir,
            max_duplicate_count=max_duplicate_count,
        )
    else:
        logging.error("Please enter a valid URL")
        SystemExit(1)


@kodekloud.command()
@click.option(
    "--output-dir",
    "-o",
    default=Path.home() / "Downloads",
    help="Output directory where quiz markdown file will be saved.",
)
@click.option(
    "--sep",
    is_flag=True,
    show_default=True,
    default=False,
    help="Write in seperate markdown files.",
)
# Function to sanitize filenames by replacing invalid characters
def sanitize_filename(filename: str) -> str:
    # Replace characters that are not allowed in filenames on Windows
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

# The main function to download the quiz
def dl_quiz(output_dir: Union[Path, str], sep: bool):
    # Ensure the output directory exists
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Call the download function, making sure to sanitize filenames
    download_quiz(output_dir, sep)

# Example of how download_quiz might work (you'd need to define this in your code)
def download_quiz(output_dir: Path, sep: bool):
    # Example for downloading and saving a quiz file
    quiz_filename = 'Are you already a collaborator?.md'
    
    # Sanitize the filename before saving
    sanitized_filename = sanitize_filename(quiz_filename)
    
    # Construct the full file path
    output_file = output_dir / sanitized_filename
    
    # Now you can safely write the file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('Quiz content goes here')
    
    print(f"Quiz downloaded and saved as {output_file}")

# Example usage
dl_quiz("KodeKloudQuiz", sep=True)


if __name__ == "__main__":
    kodekloud()
