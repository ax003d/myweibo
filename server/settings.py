import dotenv

dotenv.read_dotenv()

from getenv import env

DATA_PATH = env("DATA_PATH", "/data")
API_HOST = env("API_HOST", "localhost:8080")