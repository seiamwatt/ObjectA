import uuid
class Robot:
    def __init__(self,robot_id,robot_name,robot_type,robot_uptime,robot_downtime,robot_task,robot_id_status,robot_operational_status):
        self.name = robot_name
        self.type = robot_type
        self.uptime = robot_uptime
        self.downtime = robot_downtime
        self.task = robot_task
        self.id = robot_id
        self.id_status = robot_id_status
        self.operational_status = robot_operational_status


    def edit_name(self,new_name):
        self.name = new_name

    def edit_type(self,new_type):
        self.type = new_type

    def edit_task(self,new_task):
        self.task = new_task

    def edit_id(self,new_id):
        self.id = new_id

    def edit_operational_status(self,new_status):
        self.operational_status = new_status

    def generate_id(self):
        self.id = uuid.uuid4()
        self.id_status = True


    

    
    



    
    
    

