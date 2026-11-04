from typing import List

from pydantic import BaseModel


class Agent(BaseModel):
    agent_name: str = None
    task_list: List[Task] = []

    def add_task(self, task: Task):
        self.task_list.append(task)


class Task(BaseModel):
    task_id: int = None
    task_name: str = None
    task_description: str = None

