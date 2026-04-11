from os import getenv

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str | None = getenv("BOT_TOKEN")
DB_PATH: str = "listify.db"

# Parse allowed users from comma-separated string
ALLOWED_USERS_STR: str = getenv("ALLOWED_USERS", "")

# Flag to track if whitelist is explicitly configured AND has values
ALLOWED_USERS_ACTIVE: bool = (
    bool(ALLOWED_USERS_STR.strip()) if ALLOWED_USERS_STR is not None else False
)

# Set of allowed user IDs
ALLOWED_USERS: set[int] = set()
if ALLOWED_USERS_STR:
    ALLOWED_USERS = {
        int(uid.strip()) for uid in ALLOWED_USERS_STR.split(",") if uid.strip()
    }
