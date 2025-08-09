import os
from pypdf import PdfReader

class Me:
    def __init__(self):
        resume_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../resources/kaushik-paul-resume.pdf"))
        reader = PdfReader(resume_path)
        resume = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                resume += text

        summary_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../resources/summary.txt"))
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = f.read()

        name = "Kaushik Paul"

        self.name = name
        self.summary = summary
        self.resume = resume