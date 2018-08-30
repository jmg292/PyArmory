import uuid
import asyncio
from typing import List
from concurrent import futures
from enum import IntEnum, unique

from Command.CommandProvider import CommandProvider


@unique
class JobStatus(IntEnum):

    Completed = 0
    Pending = 1
    NotSubmitted = 2


class CommandDispatcher(object):

    def __init__(self, command_provider: CommandProvider, event_loop: asyncio.BaseEventLoop):
        self._pending_jobs = {}
        self._completed_jobs = {}
        self._event_loop = event_loop
        self._executor = futures.ThreadPoolExecutor()
        self.command_provider = command_provider

    @staticmethod
    async def parse_command(command_string: str) -> List:
        command_array = command_string.split()
        command = command_array[0].lower()
        command_array.pop(0)
        return [command, command_array]

    def job_complete_callback(self, job_id: str, command_result: str):
        if job_id in self._pending_jobs:
            del self._pending_jobs[job_id]
        self._completed_jobs[job_id] = command_result

    async def get_job_status(self, job_id: str) -> JobStatus:
        job_status = JobStatus.NotSubmitted
        if job_id in self._pending_jobs:
            job_status = JobStatus.Pending
        elif job_id in self._completed_jobs:
            job_status = JobStatus.Completed
        return job_status

    async def get_job_result(self, job_id: str) -> str:
        job_result = None
        if job_id in self._completed_jobs:
            job_result = self._completed_jobs[job_id]
            del self._completed_jobs[job_id]
        return job_result

    async def create_job(self, command_string: str) -> str:
        job_id = uuid.uuid4().hex
        command_list = await self.parse_command(command_string)
        job_container = CommandExecutionWrapper(job_id, command_list, self)
        concurrent_job = self._executor.submit(job_container.execute_command)
        self._pending_jobs[job_id] = asyncio.ensure_future(concurrent_job)
        return job_id


class CommandExecutionWrapper(object):

    def __init__(self, job_id: str, command_list: List, command_dispatcher: CommandDispatcher):
        self._job_id = job_id
        self._command_name = command_list[0]
        self._command_args = command_list[1]
        self._command_dispatcher = command_dispatcher

    def execute_command(self):
        try:
            command_result = self._command_dispatcher.command_provider.execute_command(
                                self._command_name,
                                *self._command_args
                             )
        except Exception as e:
            command_result = str(e)
        self._command_dispatcher.job_complete_callback(self._job_id, command_result)
