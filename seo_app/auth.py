"""Băm và kiểm tra mật khẩu đăng nhập.

Dùng PBKDF2-SHA256 có sẵn trong thư viện chuẩn Python, không cần cài thêm gì.
Mã băm có dạng ``pbkdf2_sha256:<số vòng>:<salt hex>:<hash hex>``. Không dùng ký
tự ``$`` để tránh bị hiểu nhầm là biến khi đọc file ``.env``.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets

ALGORITHM = "pbkdf2_sha256"
DEFAULT_ITERATIONS = 600_000
SALT_BYTES = 16


def hash_password(password: str, *, iterations: int = DEFAULT_ITERATIONS) -> str:
    """Tạo mã băm cho mật khẩu (mỗi lần gọi ra một mã khác nhau nhờ salt ngẫu nhiên)."""
    if not password:
        raise ValueError("Mật khẩu không được để trống.")
    salt = secrets.token_bytes(SALT_BYTES)
    digest = _derive(password, salt, iterations)
    return f"{ALGORITHM}:{iterations}:{salt.hex()}:{digest.hex()}"


def verify_password(password: str, stored_hash: str | None) -> bool:
    """Kiểm tra mật khẩu với mã băm đã lưu. Mã băm sai định dạng thì trả về False."""
    parsed = _parse(stored_hash)
    if not password or parsed is None:
        return False
    iterations, salt, expected = parsed
    actual = _derive(password, salt, iterations)
    return hmac.compare_digest(actual, expected)


def is_valid_hash(stored_hash: str | None) -> bool:
    """Mã băm có đúng định dạng không (không kiểm tra mật khẩu)."""
    return _parse(stored_hash) is not None


def _parse(stored_hash: str | None) -> tuple[int, bytes, bytes] | None:
    if not stored_hash:
        return None
    parts = stored_hash.strip().split(":")
    if len(parts) != 4 or parts[0] != ALGORITHM:
        return None
    try:
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        digest = bytes.fromhex(parts[3])
    except ValueError:
        return None
    if iterations <= 0 or not salt or not digest:
        return None
    return iterations, salt, digest


def _derive(password: str, salt: bytes, iterations: int) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
