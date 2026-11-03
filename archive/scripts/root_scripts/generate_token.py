from datetime import datetime, timedelta, timezone
from jose import jwt

to_encode = {
    "sub": "frontend",
    "role": "admin",
    "exp": datetime.now(timezone.utc) + timedelta(days=3650),
    "iat": datetime.now(timezone.utc)
}
encoded_jwt = jwt.encode(to_encode, "change-this-to-a-different-random-secret-key", algorithm="HS256")
print(encoded_jwt)
