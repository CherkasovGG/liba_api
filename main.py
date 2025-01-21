import os
import uvicorn
from dotenv import load_dotenv

load_dotenv(override=True)

DEBUG: bool = os.environ.get("DEBUG", "False") == "True"
API_HOST: str = os.environ.get("APP_HOST", "0.0.0.0")
API_PORT: int = int(os.environ.get("APP_PORT", "8000"))
DB_URL: str = os.environ.get("DB_URL")
JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY")

if __name__ == "__main__":
    uvicorn.run(
        app="API_for_library.api:api",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        workers=1,
    )
