import hashlib
import hmac
import secrets
import base64


# Password hashing settings
SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1


def hash_password(password: str) -> str:

    if not isinstance(password, str) or not password:
        raise ValueError("Password cannot be empty")

    if len(password) > 1024:
        raise ValueError("Password is too long")

    # Generate a random salt
    salt = secrets.token_bytes(16)

    # Generate the password hash
    password_hash = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        dklen=64
    )

    # Convert salt and hash into readable text
    salt_text = base64.b64encode(salt).decode("utf-8")
    hash_text = base64.b64encode(password_hash).decode("utf-8")

    # Store algorithm settings with the hash
    return (
        f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}"
        f"${salt_text}${hash_text}"
    )


def verify_password(password: str, stored_hash: str) -> bool:

    if not isinstance(password, str):
        return False

    if not isinstance(stored_hash, str):
        return False

    try:
        algorithm, n, r, p, salt_text, hash_text = stored_hash.split("$")

        if algorithm != "scrypt":
            return False

        n = int(n)
        r = int(r)
        p = int(p)

        # Reject unexpected or unsafe parameters
        if n != SCRYPT_N or r != SCRYPT_R or p != SCRYPT_P:
            return False

        salt = base64.b64decode(salt_text, validate=True)
        expected_hash = base64.b64decode(hash_text, validate=True)

        if len(salt) != 16 or len(expected_hash) != 64:
            return False

        # Hash the entered password using the original salt
        new_hash = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=n,
            r=r,
            p=p,
            dklen=64
        )

        # Compare hashes safely
        return hmac.compare_digest(new_hash, expected_hash)

    except (ValueError, TypeError, UnicodeError):
        return False