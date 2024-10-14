from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(entered_password, hashed_password):
    return pwd_context.verify(entered_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)
