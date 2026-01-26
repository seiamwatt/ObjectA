import PyPDF2


class Helper:

    def __init__(self, name="Helper"):
        self.name = name

    def load_pdf(self, file_path):
        """Extracts text from every page of a PDF."""
        try:
            text = ""
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)

                for page in pdf_reader.pages:
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except Exception:
                        continue

            return text

        except Exception as e:
            print(f"Error loading PDF: {e}")
            return None



    def load_txt(self, file_path):
        """Loads a text file."""
        try:
            with open(file_path, "r") as file:
                return file.read()
        except Exception as e:
            print(f"Error loading text file: {e}")
            return None



    def prompt(self):
        """Returns a prompt template."""
        input_prompt = ""
        return input_prompt



    def help_FAQ(self, file_path):
        """Returns help documentation."""
        help_text = ""
        return help_text