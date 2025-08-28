import utils
import uuid

# task object instances

class Type(Enum):
    NORM = 0
    RESEARCH = 1


class Task:
    
    def __init__(self,title,description,id,due_date,time_to_due_date,type,completion_status):
        self.title = title
        self.description = description
        self.completion_status = completion_status
        self.id = self.generate_ID
        self.due_date = due_date
        self.time_to_due_date = time_to_due_date
        self.type = type



    def generate_ID():
        return uuid.uuid4()
    
    def set_completion_status(self,completion_status):
        self.completion_status = completion_status

    def time_till_due():
        return

    def is_overdue():
        return

    def set_type(new_type):
        return new_type
    





        


    