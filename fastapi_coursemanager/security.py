from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "your_super_secret_key_change_this"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def get_password_hash(password: str):

    """
    bcrypt is intentionally slow.

    Unlike MD5 or SHA256,
    bcrypt protects passwords against
    brute-force attacks.
    """

    return pwd_context.hash(password)


def verify_password(
    plain_password,
    hashed_password
):

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update(
        {"exp": expire}
    )

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login/"
)


def decode_access_token(token: str):

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:

        return None     