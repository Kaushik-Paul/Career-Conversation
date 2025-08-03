from pypdf import PdfReader

class Me:
    def __init__(self):
        reader = PdfReader("../resources/kaushik-paul-resume.pdf")
        resume = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                resume += text

        with open("../resources/summary.txt", "r", encoding="utf-8") as f:
            summary = f.read()

        name = "Kaushik Paul"

        self.name = name
        self.summary = summary
        self.resume = resume