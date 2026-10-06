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
from seo_app.config import DEFAULT_ENV_FILE, PROJECT_ROOT

KEY = "APP_PASSWORD_HASH"
MIN_LENGTH = 8


def set_env_value(env_file: Path, key: str, value: str, template: Path | None = None) -> None:
    """Ghi ``key=value`` vào file .env: thay dòng cũ nếu có, không thì thêm vào cuối.

    Nếu .env chưa tồn tại và có ``template`` (.env.example) thì sao chép template trước.
    """
    if not env_file.exists() and template is not None and template.is_file():
        shutil.copyfile(template, env_file)

    lines = env_file.read_text(encoding="utf-8").splitlines() if env_file.exists() else []
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
    env_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


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

    try:
        password = ask_password()
    except (KeyboardInterrupt, EOFError):
        print("\nĐã hủy.")
        return 1

    hashed = hash_password(password)
    if args.print:
        print(f"\nDán dòng sau vào file .env:\n{KEY}={hashed}")
        return 0

    set_env_value(DEFAULT_ENV_FILE, KEY, hashed, template=PROJECT_ROOT / ".env.example")
    print(f"\nĐã lưu mật khẩu mới vào {DEFAULT_ENV_FILE}.")
    print("Nếu app đang chạy, hãy tải lại trang (F5) rồi đăng nhập bằng mật khẩu mới.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
