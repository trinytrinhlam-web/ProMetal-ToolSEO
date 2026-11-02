"""Đặt mật khẩu đăng nhập cho app.

Cách chạy (ở thư mục dự án):
    uv run python scripts/hash_password.py          # hỏi mật khẩu rồi ghi mã băm vào .env
    uv run python scripts/hash_password.py --print  # chỉ in mã băm, không ghi file

Trên Windows có thể bấm đúp set_password.bat, trên Mac bấm đúp set_password.command.
Mật khẩu không được lưu ở đâu cả; .env chỉ giữ mã băm.

Máy có biến môi trường APP_PASSWORD_HASH (app dùng biến đó trước .env) thì dừng trước khi hỏi
mật khẩu và chỉ cách gỡ biến, vì ghi .env lúc đó không có tác dụng (T-105).
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
    EnvFileReadBackError,
    EnvFileReadError,
    EnvFileWriteError,
    password_hash_overridden,
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
# Ghi xong mà đọc lại để kiểm không được (chương trình khác giữ file đúng lúc đó; SL-T104-1, T-105):
# nói đúng nguyên nhân, không nói tới dòng sai định dạng. Bộ ghi đã bỏ bản vừa ghi.
MSG_ENV_READBACK = (
    "Không đọc lại được file .env để kiểm sau khi ghi ({error}) nên đã bỏ bản vừa ghi. File .env "
    "cũ vẫn còn nguyên. Đóng chương trình đang mở file (ví dụ phần mềm diệt virus hay đồng bộ thư "
    "mục) rồi chạy lại set_password."
)
# Như trên mà bỏ bản vừa ghi cũng không được: .env có thể đã mang mật khẩu mới, chưa kiểm.
MSG_ENV_READBACK_UNSURE = (
    "Không đọc lại được file .env để kiểm sau khi ghi ({error}), cũng không bỏ được bản vừa ghi: "
    "file .env có thể đã mang mật khẩu mới nhưng chưa được kiểm. Đóng chương trình đang mở file "
    "(ví dụ phần mềm diệt virus hay đồng bộ thư mục) rồi chạy lại set_password để ghi lại cho chắc."
)
# Biến môi trường APP_PASSWORD_HASH của máy đè .env (``load_settings``; SL-T104-2, T-105): dừng
# trước khi hỏi mật khẩu. Câu cố định, không in giá trị biến. Phải tắt hẳn app vì app đang chạy
# vẫn giữ biến đó tới khi mở lại.
MSG_ENV_OVERRIDDEN = (
    f"Máy này đang có biến môi trường {KEY} (một cài đặt của Windows hay Mac, nằm ngoài file "
    ".env). App luôn dùng giá trị trong biến đó trước file .env, nên mật khẩu mới ghi vào .env sẽ "
    "không có hiệu lực.\n"
    "Cách sửa:\n"
    f"1. Gỡ biến {KEY} khỏi máy. Windows: bấm Start, gõ «environment variables» (Windows tiếng "
    "Việt: «biến môi trường»), mở «Edit environment variables for your account» (Chỉnh sửa biến "
    f"môi trường cho tài khoản của bạn), chọn dòng {KEY}, bấm Delete rồi OK; không thấy dòng đó "
    "thì có thể nó nằm ở phần biến của hệ thống (cần quyền quản trị). Mac: xóa dòng có "
    f"{KEY} trong file ~/.zshrc.\n"
    "2. Nếu app đang chạy: tắt hẳn app (đóng cửa sổ đen hay Terminal của app).\n"
    "3. Chạy lại set_password."
)
MSG_PRINT_OVERRIDDEN = (
    f"Lưu ý: máy này đang có biến môi trường {KEY}. App dùng giá trị trong biến đó trước file "
    ".env, nên dòng trên dán vào .env sẽ chưa có hiệu lực: gỡ biến đó khỏi máy rồi tắt hẳn app và "
    "mở lại (cách gỡ: chạy set_password không kèm --print)."
)


class UnsureSaveError(ConfigError):
    """Chưa chắc mật khẩu mới đã được lưu: ghi xong mà không đọc lại được để kiểm, cũng không bỏ
    được bản vừa ghi (SL-T104-1, T-105). ``main`` báo «Chưa chắc đã lưu…», không «Chưa lưu…»."""


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
    hay ghi được .env thì ``ConfigError`` câu cố định; ghi lỗi thì .env cũ còn nguyên. Ghi xong mà
    không đọc lại được để kiểm, cũng không bỏ được bản vừa ghi, thì ``UnsureSaveError`` (T-105).
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
    except EnvFileReadBackError as exc:
        if exc.restored:
            raise ConfigError(MSG_ENV_READBACK.format(error=exc.error_name)) from exc
        raise UnsureSaveError(MSG_ENV_READBACK_UNSURE.format(error=exc.error_name)) from exc
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
    overridden = password_hash_overridden()  # chỉ đúng/sai, không đọc giá trị biến

    if not args.print:
        if overridden:  # ghi .env cũng vô ích: báo ngay, chưa bắt gõ mật khẩu
            print(f"Chưa đặt được mật khẩu. {MSG_ENV_OVERRIDDEN}")
            return 1
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
        if overridden:
            print(f"\n{MSG_PRINT_OVERRIDDEN}")
        return 0

    try:
        set_env_value(DEFAULT_ENV_FILE, KEY, hashed, template=PROJECT_ROOT / ".env.example")
    except UnsureSaveError as exc:
        print(f"\nChưa chắc đã lưu được mật khẩu mới. {exc}")
        return 1
    except ConfigError as exc:
        print(f"\nChưa lưu mật khẩu mới. {exc}")
        return 1
    print(f"\nĐã lưu mật khẩu mới vào {DEFAULT_ENV_FILE}.")
    print("Nếu app đang chạy, hãy tải lại trang (F5) rồi đăng nhập bằng mật khẩu mới.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
