import os

from supabase import create_client
from common.logger import setup_logger


class SupabaseClient:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.logger = setup_logger("supabase_client")
        self._URL = os.getenv("SUPABASE_URL")
        self._KEY = os.getenv("SUPABASE_KEY")
        self.client = create_client(self._URL, self._KEY)

    def upload_file(self, file_path: str, bucket: str, db_path: str):
        self.logger.info(f"Uploading {file_path} to bucket {bucket} as {db_path}")
        with open(file_path, 'rb') as file:
            response = self.client.storage.from_(bucket).upload(db_path, file)
            self.logger.info(response)
