"""Đặt mật khẩu đăng nhập cho app.

Cách chạy (ở thư mục dự án):
    uv run python scripts/hash_password.py          # hỏi mật khẩu rồi ghi mã băm vào .env
    uv run python scripts/hash_password.py --print  # chỉ in mã băm, không ghi file

Trên Windows có thể bấm đúp set_password.bat, trên Mac bấm đúp set_password.command.
Mật khẩu không được lưu ở đâu cả; .env chỉ giữ mã băm.
"""

from __future__ import annotations

import argparse
import getpass
import re
import shutil
import sys
from pathlib import Path

from seo_app.auth import hash_password
from seo_app.config import DEFAULT_ENV_FILE, ENV_RESAVE_UTF8, PROJECT_ROOT, ConfigError
from seo_app.env_file import (
    PASSWORD_HASH_VAR,
    EnvFileError,
    EnvFileFormatError,
    EnvFileReadError,
    EnvFileWriteError,
    set_password_hash,
)

KEY = PASSWORD_HASH_VAR
MIN_LENGTH = 8
# Câu cố định khi không đọc, ghi được .env (SL-T084-1, T-090): không traceback, không đường dẫn,
# không nội dung .env, không câu lỗi gốc.
MSG_ENV_NOT_UTF8 = f"{ENV_RESAVE_UTF8} rồi chạy lại set_password."
MSG_ENV_UNREADABLE = (
    "Không đọc được file .env ({error}). Đóng chương trình đang mở file (nếu có), kiểm tra quyền "
    "đọc file rồi chạy lại set_password."
)
# Chép .env.example thành .env (chưa có .env) không được: không có file cũ nào để nói «còn nguyên».
MSG_ENV_UNWRITABLE = (
    "Không ghi được file .env ({error}). Đóng chương trình đang mở file (nếu có), kiểm tra quyền "
    "ghi file rồi chạy lại set_password."
)
# Ghi mã băm không được: bộ ghi ghi file tạm rồi mới thay (T-104, LC-T090-2), nên .env cũ chưa bị
# đụng tới.
MSG_ENV_KEPT = (
    "Không ghi được file .env ({error}). File .env cũ vẫn còn nguyên. Đóng chương trình đang mở "
    "file (nếu có), kiểm tra quyền ghi file rồi chạy lại set_password."
)
MSG_ENV_FORMAT = (
    "File .env có dòng sai định dạng nên chưa ghi được mật khẩu mới; file .env cũ vẫn còn nguyên. "
    "Mở .env, sửa dòng đó (thường là thiếu dấu nháy đóng) rồi chạy lại set_password."
)
# Xuống dòng đúng như python-dotenv (app) đọc: chỉ CR, LF (không cắt ở FF, VT, NEL, U+2028…).
_DOTENV_LINES = re.compile(r"\r\n|\r|\n")


def read_env_lines(env_file: Path) -> list[str]:
    """Các dòng của .env (rỗng nếu chưa có file), tách đúng như python-dotenv (chỉ CR, LF). Dùng để
    kiểm .env đọc được trước khi hỏi mật khẩu. File lưu sai bảng mã (Notepad «ANSI», UTF-16) hay
    không đọc được thì ``ConfigError`` câu cố định."""
    try:
        if not env_file.exists():
            return []
        text = env_file.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ConfigError(MSG_ENV_NOT_UTF8) from exc
    except OSError as exc:
        raise ConfigError(MSG_ENV_UNREADABLE.format(error=type(exc).__name__)) from exc
    lines = _DOTENV_LINES.split(text)
    return lines[:-1] if lines and not lines[-1] else lines


def set_env_value(env_file: Path, key: str, value: str, template: Path | None = None) -> None:
    """Ghi mã băm ``key=value`` vào file .env bằng bộ ghi của ``seo_app.env_file``
    (``set_password_hash``; T-104, LC-T090-1, -2): thay **mọi** dòng của biến (app dùng dòng
    cuối), giữ nguyên mọi dòng khác, ghi file tạm rồi thay nguyên tử. Chưa có dòng thì thêm cuối.

    Nếu .env chưa tồn tại và có ``template`` (.env.example) thì sao chép template trước. Không đọc
    hay ghi được .env thì ``ConfigError`` câu cố định; ghi lỗi thì .env cũ còn nguyên.
    """
    if key != KEY:
        raise ValueError("set_password chỉ ghi APP_PASSWORD_HASH.")
    try:
        if not env_file.exists() and template is not None and template.is_file():
            shutil.copyfile(template, env_file)
    except OSError as exc:
        raise ConfigError(MSG_ENV_UNWRITABLE.format(error=type(exc).__name__)) from exc

    try:
        set_password_hash(value, env_file)
    except EnvFileWriteError as exc:
        raise ConfigError(MSG_ENV_KEPT.format(error=exc.error_name)) from exc
    except EnvFileReadError as exc:
        if exc.not_utf8:
            raise ConfigError(MSG_ENV_NOT_UTF8) from exc
        raise ConfigError(MSG_ENV_UNREADABLE.format(error=exc.error_name)) from exc
    except EnvFileFormatError as exc:
        raise ConfigError(MSG_ENV_FORMAT) from exc
    except EnvFileError as exc:  # câu cố định của bộ ghi (liên kết tắt, dòng thiếu nháy…)
        raise ConfigError(str(exc)) from exc


def ask_password() -> str:
    while True:
        password = getpass.getpass("Nhập mật khẩu mới (gõ sẽ không hiện chữ): ")
        if len(password) < MIN_LENGTH:
            print(f"Mật khẩu cần ít nhất {MIN_LENGTH} ký tự. Thử lại.\n")
            continue
        again = getpass.getpass("Nhập lại mật khẩu: ")
        if password != again:
            print("Hai lần nhập không khớp. Thử lại.\n")
            continue
        return password


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Tạo mã băm mật khẩu đăng nhập cho SEO App.")
    parser.add_argument("--print", action="store_true", help="chỉ in mã băm, không ghi vào .env")
    args = parser.parse_args(argv)

    if not args.print:
        try:
            read_env_lines(DEFAULT_ENV_FILE)  # .env hỏng thì báo ngay, chưa bắt gõ mật khẩu
        except ConfigError as exc:
            print(f"Chưa đặt được mật khẩu. {exc}")
            return 1

    try:
        password = ask_password()
    except (KeyboardInterrupt, EOFError):
        print("\nĐã hủy.")
        return 1

    hashed = hash_password(password)
    if args.print:
        print(f"\nDán dòng sau vào file .env:\n{KEY}={hashed}")
        return 0

    try:
        set_env_value(DEFAULT_ENV_FILE, KEY, hashed, template=PROJECT_ROOT / ".env.example")
    except ConfigError as exc:
        print(f"\nChưa lưu mật khẩu mới. {exc}")
        return 1
    print(f"\nĐã lưu mật khẩu mới vào {DEFAULT_ENV_FILE}.")
    print("Nếu app đang chạy, hãy tải lại trang (F5) rồi đăng nhập bằng mật khẩu mới.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
