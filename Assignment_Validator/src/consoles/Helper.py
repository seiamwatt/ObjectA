class Helper:

    def __init__(self,name = "Helper"):
        self.name = name

    # load_pdf - tries to extract every page
    def load_pdf(self,file_path):
        try:
            text = " "
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)

                for page_num in len(num_pages):

                    try:
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()

                        if page_text:
                            text += page_text + "\n"

                    except Exception as e:
                        continue 
            return text

        except Exception as e:
            return None
        


    # List of commands for user, other instructions/documentations
    def help_FAQ(self,file_path):
        
        help_text = ""

        return help_text