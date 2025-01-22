import os
import asyncio
from .Database import Database
from ..models_interfaces.Llama import LlamaTextQuery

DEFAULT_QUERIES = ['generate an e-mail']
DEFAULT_NUM_EMAILS_TO_GEN = 10
DEFAULT_MAX_CONCURRENT_REQUESTS = 10

class DatabaseEmails(Database):
    def __init__(self, path: str):
        self.database_path = path
        self.num_emails = 0
        self.generation_options = {
            'include_history': False,
            'consider_history': False
        }
        self.semaphore = asyncio.Semaphore(DEFAULT_MAX_CONCURRENT_REQUESTS)

    def create_folder(self) -> None:
        return super().create_folder()

    def build(self, queries: list[str] = DEFAULT_QUERIES, num_emails_to_gen: int = DEFAULT_NUM_EMAILS_TO_GEN):
        generated_emails = asyncio.run(self._generate_emails(queries, num_emails_to_gen))
        print(generated_emails[0]) # debug

    async def _generate_emails(self, queries: list[str] = DEFAULT_QUERIES, num_emails_to_gen: int = DEFAULT_NUM_EMAILS_TO_GEN):
        tasks = []
        for query in queries:
            for n in range(num_emails_to_gen):
                tasks.append(self._llama_api_call_limited(query, n))
        generated_emails = await asyncio.gather(*tasks)
        return generated_emails

    async def _llama_api_call_limited(self, query: str, call_number: int = 0):
        async with self.semaphore:
            return await self._llama_text_call(query, call_number)

    async def _llama_text_call(self, query: str, call_number: int = 0):
        query_obj = LlamaTextQuery()
        print(f"Generating for query \"{query}\", call {call_number} ...\n")
        response = await asyncio.to_thread(
            query_obj.query,
            query,
            self.generation_options['include_history'],
            self.generation_options['consider_history']
            )
        print(f"Response for query \"{query}\", call {call_number} has been generated!\n")
        self.num_emails += 1
        return response['content']
    
    def store(self):
        return super().store()
    
    def print(self):
        return super().print()
    
    def set_max_concurrent_requests(self, max_concurrent_requests: int = DEFAULT_MAX_CONCURRENT_REQUESTS):
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)