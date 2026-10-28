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
import shutil
import sys
from pathlib import Path

from seo_app.auth import hash_password
from seo_app.config import DEFAULT_ENV_FILE, ENV_RESAVE_UTF8, PROJECT_ROOT, ConfigError

KEY = "APP_PASSWORD_HASH"
MIN_LENGTH = 8
# Câu cố định khi không đọc, ghi được .env (SL-T084-1, T-090): không traceback, không đường dẫn,
# không nội dung .env, không câu lỗi gốc.
MSG_ENV_NOT_UTF8 = f"{ENV_RESAVE_UTF8} rồi chạy lại set_password."
MSG_ENV_UNREADABLE = (
    "Không đọc được file .env ({error}). Đóng chương trình đang mở file (nếu có), kiểm tra quyền "
    "đọc file rồi chạy lại set_password."
)
MSG_ENV_UNWRITABLE = (
    "Không ghi được file .env ({error}). Đóng chương trình đang mở file (nếu có), kiểm tra quyền "
    "ghi file rồi chạy lại set_password."
)


def read_env_lines(env_file: Path) -> list[str]:
    """Các dòng của .env (rỗng nếu chưa có file). File lưu sai bảng mã (Notepad «ANSI», UTF-16) hay
    không đọc được thì ``ConfigError`` câu cố định."""
    try:
        if not env_file.exists():
            return []
        return env_file.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise ConfigError(MSG_ENV_NOT_UTF8) from exc
    except OSError as exc:
        raise ConfigError(MSG_ENV_UNREADABLE.format(error=type(exc).__name__)) from exc


def set_env_value(env_file: Path, key: str, value: str, template: Path | None = None) -> None:
    """Ghi ``key=value`` vào file .env: thay dòng cũ nếu có, không thì thêm vào cuối.

    Nếu .env chưa tồn tại và có ``template`` (.env.example) thì sao chép template trước. Không đọc
    hay ghi được .env thì ``ConfigError`` câu cố định (``read_env_lines``, ``MSG_ENV_UNWRITABLE``).
    """
    try:
        if not env_file.exists() and template is not None and template.is_file():
            shutil.copyfile(template, env_file)
    except OSError as exc:
        raise ConfigError(MSG_ENV_UNWRITABLE.format(error=type(exc).__name__)) from exc

    lines = read_env_lines(env_file)
    new_line = f"{key}={value}"
    replaced = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(f"{key}=") or stripped.startswith(f"export {key}="):
            lines[i] = new_line
            replaced = True
            break
    if not replaced:
        lines.append(new_line)
    try:
        env_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError as exc:
        raise ConfigError(MSG_ENV_UNWRITABLE.format(error=type(exc).__name__)) from exc


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
