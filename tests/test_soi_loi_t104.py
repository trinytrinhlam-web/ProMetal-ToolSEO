"""Soi Lỗi T-104: ``set_password`` ghi ``.env`` an toàn (LC-T090-1, LC-T090-2).

Ngoài test của Thợ Máy (``tests/test_t104_set_password.py``) và Lá Chắn T-090:

- ma trận ``.env`` lạ (ba dòng mã băm có ``export``, dấu cách, nháy; mã băm có nháy kèm chú thích;
  dòng chỉ có tên biến; dòng chú thích giống mã băm; BOM; CR kiểu Mac cũ; CRLF trộn LF; không
  xuống dòng cuối; file rỗng; nháy mở không đóng ở biến khác; dòng mã băm giả nằm trong giá trị
  nhiều dòng; biến khác tham chiếu mã băm; FF, VT, NEL, U+2028, U+2029, RS, NUL, tab trong giá trị)
  và 300 ``.env`` ngẫu nhiên: mật khẩu mới có hiệu lực đúng như app đọc, biến khác giữ nguyên, không
  sót file tạm; không ghi được thì file giữ nguyên từng byte;
- lỗi ghi thật và giả ở từng bước: ổ đầy giữa lúc ghi file tạm, ``flush`` lỗi, không tạo được file
  tạm, ``.env`` đang được chương trình khác mở (Windows từ chối ``os.replace``), ``.env`` chỉ đọc.

Lỗi tìm được: ``xfail(strict=True)`` mã SL-T104-x (``docs/team/reports/T-104-soi-loi.md``). Ký tự
lạ viết bằng ``chr(…)``; ``.env`` giả trong thư mục tạm, mật khẩu giả ghép lúc chạy.
"""

from __future__ import annotations

import errno
import io
import os
import random
import stat
from pathlib import Path

import pytest
from dotenv import dotenv_values
from test_hash_password_script import load_script

import seo_app.env_file as env_file
from seo_app.auth import hash_password, verify_password
from seo_app.config import load_settings

KEY = "APP_PASSWORD_HASH"
IS_WINDOWS = os.name == "nt"
NEW_PASSWORD = "-".join(["mat", "khau", "moi", "soi", "loi"])
OLD = hash_password("-".join(["cu", "T104"]), iterations=1_000)
BOM = chr(0xFEFF)
OTHER = f"WORDPRESS_URL=https://a.vn\n{KEY}={OLD}\nIMAGE_FOLDERS=D:/Anh\n"


def run_set_password(project_root, monkeypatch, env: Path) -> tuple[int, str]:
    script = load_script(project_root)
    monkeypatch.setattr(script, "DEFAULT_ENV_FILE", env)
    monkeypatch.setattr(script.getpass, "getpass", lambda prompt="": NEW_PASSWORD)
    monkeypatch.setattr(script, "hash_password", lambda p: hash_password(p, iterations=1_000))
    out = io.StringIO()
    monkeypatch.setattr("sys.stdout", out)
    code = script.main([])
    return code, out.getvalue().strip()


def others(raw: bytes) -> dict[str, str | None]:
    text = raw.decode("utf-8")
    return {k: v for k, v in dotenv_values(stream=io.StringIO(text)).items() if k != KEY}


def leftovers(folder: Path) -> list[str]:
    return sorted(p.name for p in folder.iterdir() if p.name.endswith(".tmp"))


def new_password_active(env: Path) -> bool:
    return verify_password(NEW_PASSWORD, load_settings(env_file=env, environ={}).password_hash)


# ======================================================== ma trận .env lạ: mật khẩu mới có hiệu lực

CASES = {
    "ba-dong-export-cach-nhay": f"{KEY}=a\nexport {KEY} = b\n  {KEY}='{OLD}'\n",
    "nhay-kep-kem-chu-thich": f'{KEY}="{OLD}" # mat khau cu\nY=2\n',
    "chi-ten-bien": f"{KEY}\nZ=3\n",
    "chu-thich-giong-ma-bam": f"# {KEY}={OLD}\nA=1\n",
    "bom-ma-bam-dong-dau-crlf": f"{BOM}{KEY}={OLD}\r\nB=2\r\n",
    "bom-chua-co-ma-bam": f"{BOM}B=2\r\n",
    "cr-kieu-mac-cu": f"A=1\r{KEY}={OLD}\rB=2\r",
    "crlf-tron-lf": f"A=1\r\n{KEY}={OLD}\nB=2\r\n",
    "khong-xuong-dong-cuoi": f"A=1\n{KEY}={OLD}",
    "file-rong": "",
    "chi-chu-thich": "# chi chu thich\n",
    "nhay-mo-khong-dong-o-bien-khac": f'W="abc\n{KEY}={OLD}\n',
    "ma-bam-gia-trong-gia-tri-nhieu-dong": f'N="a\n{KEY}=gia\nb"\n{KEY}={OLD}\n',
    "ky-tu-la-trong-gia-tri": "V=a"
    + "".join(chr(c) + "x" for c in (0x0C, 0x0B, 0x85, 0x2028, 0x2029, 0x1E))
    + f"\n{KEY}={OLD}\n",
    "nul-trong-gia-tri": f"V=a{chr(0)}b\n{KEY}={OLD}\n",
    "tab-cuoi-dong": f"A=1\t \n{KEY}={OLD}\t\n",
}


@pytest.mark.parametrize("text", CASES.values(), ids=CASES.keys())
def test_new_password_active_and_other_values_kept(project_root, tmp_path, monkeypatch, text):
    """Mật khẩu mới có hiệu lực đúng như app đọc (python-dotenv, dòng cuối thắng), mọi biến khác
    giữ nguyên giá trị, không sót file tạm."""
    raw = text.encode("utf-8")
    env = tmp_path / ".env"
    env.write_bytes(raw)
    code, out = run_set_password(project_root, monkeypatch, env)
    assert code == 0, out
    assert new_password_active(env)
    assert others(env.read_bytes()) == others(raw)
    assert leftovers(tmp_path) == []
    assert env.read_bytes().startswith(BOM.encode()) == raw.startswith(BOM.encode())


def test_other_value_referencing_hash_follows_new_hash(project_root, tmp_path, monkeypatch):
    """Biến khác tham chiếu ``${APP_PASSWORD_HASH}``: app đọc ra mã băm mới (đúng như python-dotenv
    thế biến), không phải bản cũ."""
    env = tmp_path / ".env"
    env.write_bytes(f"{KEY}={OLD}\nREF=${{{KEY}}}\n".encode())
    code, _ = run_set_password(project_root, monkeypatch, env)
    assert code == 0 and new_password_active(env)
    values = dotenv_values(env, encoding="utf-8")
    assert values["REF"] == values[KEY] != OLD


PIECES = [
    f"{KEY}={{h}}",
    f"export {KEY}={{h}}",
    f"{KEY} = {{h}}",
    f"{KEY}='{{h}}'",
    f'{KEY}="{{h}}"',
    "A=1",
    "B='x y'",
    'C="m\nn"',
    "# chu thich",
    "",
    "D=" + chr(0x0C) + "z",
    "E=" + chr(0x2028),
    "F=a#b",
    "G=  sp  ",
    'H="q\\"r"',
    "I=${A}",
    "export J=1",
    "K=" + chr(0x85) + "k",
]


def test_random_env_files(project_root, tmp_path, monkeypatch):
    """300 ``.env`` ngẫu nhiên (cố định hạt giống): ghi được thì mật khẩu mới có hiệu lực, biến khác
    giữ nguyên, không sót file tạm; không ghi được thì file giữ nguyên từng byte."""
    rnd = random.Random(104)
    for i in range(300):
        lines = [rnd.choice(PIECES).replace("{h}", OLD) for _ in range(rnd.randint(0, 8))]
        newline = rnd.choice(["\n", "\r\n"])
        text = (BOM if rnd.random() < 0.2 else "") + newline.join(lines)
        text += newline if rnd.random() < 0.7 else ""
        raw = text.encode("utf-8")
        folder = tmp_path / str(i)
        folder.mkdir()
        env = folder / ".env"
        env.write_bytes(raw)
        code, out = run_set_password(project_root, monkeypatch, env)
        assert leftovers(folder) == [], text
        if code == 0:
            assert new_password_active(env), text
            assert others(env.read_bytes()) == others(raw), text
        else:
            assert env.read_bytes() == raw, (text, out)


# =================================================== lỗi ghi ở từng bước: file cũ còn nguyên


class _Wrapped:
    """Bọc file tạm thật của bộ ghi để giả lỗi đúng lúc ghi (file thật vẫn được đóng)."""

    def __init__(self, fh, fail_write: bool):
        self.fh = fh
        self.fail_write = fail_write

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.fh.close()
        return False

    def write(self, text):
        if self.fail_write:  # ổ đầy: ghi được một nửa rồi lỗi
            self.fh.write(text[: len(text) // 2])
            self.fh.flush()
            raise OSError(errno.ENOSPC, "No space left on device")
        return self.fh.write(text)

    def flush(self):
        if not self.fail_write:
            raise OSError(errno.EIO, "I/O error")
        self.fh.flush()

    def fileno(self):
        return self.fh.fileno()


def _fail_at(monkeypatch, how: str) -> None:
    real_fdopen = os.fdopen
    if how in ("o-day", "flush"):
        monkeypatch.setattr(
            env_file.os,
            "fdopen",
            lambda fd, *a, **k: _Wrapped(real_fdopen(fd, *a, **k), fail_write=how == "o-day"),
        )
    elif how == "file-tam":

        def refuse(*a, **k):
            raise PermissionError(13, "Permission denied")

        monkeypatch.setattr(env_file.tempfile, "mkstemp", refuse)


@pytest.mark.parametrize("how", ["o-day", "flush", "file-tam"])
def test_write_fault_keeps_env_and_tells_truth(project_root, tmp_path, monkeypatch, how):
    """Ổ đầy giữa lúc ghi file tạm, ``flush`` lỗi, không tạo được file tạm: ``.env`` cũ giữ nguyên
    từng byte, file tạm được dọn, câu báo cố định nói file cũ còn nguyên, không đường dẫn."""
    env = tmp_path / ".env"
    env.write_bytes(OTHER.encode())
    _fail_at(monkeypatch, how)
    code, out = run_set_password(project_root, monkeypatch, env)
    assert code == 1
    assert env.read_bytes() == OTHER.encode()
    assert leftovers(tmp_path) == []
    assert "File .env cũ vẫn còn nguyên" in out
    assert str(tmp_path) not in out and "Traceback" not in out and "No space" not in out


@pytest.mark.skipif(not IS_WINDOWS, reason="Windows từ chối thay file đang mở hay chỉ đọc")
@pytest.mark.parametrize("how", ["dang-mo", "chi-doc"])
def test_real_windows_refusal_keeps_env(project_root, tmp_path, monkeypatch, how):
    """Lỗi thật của Windows ở bước ``os.replace``: ``.env`` đang được chương trình khác mở (không
    cho xóa, thay), hay có thuộc tính chỉ đọc. Bước kiểm đầu đọc được nên người dùng đã gõ mật
    khẩu; sau đó báo «File .env cũ vẫn còn nguyên», file giữ nguyên từng byte, không sót file
    tạm."""
    env = tmp_path / ".env"
    env.write_bytes(OTHER.encode())
    holder = None
    if how == "dang-mo":
        holder = env.open("rb")
    else:
        os.chmod(env, stat.S_IREAD)
    try:
        code, out = run_set_password(project_root, monkeypatch, env)
    finally:
        if holder is not None:
            holder.close()
        os.chmod(env, stat.S_IREAD | stat.S_IWRITE)
    assert code == 1
    assert "Không ghi được file .env (PermissionError). File .env cũ vẫn còn nguyên" in out
    assert env.read_bytes() == OTHER.encode()
    assert leftovers(tmp_path) == []


# ================================= SL-T104-1: đọc lại sau khi thay lỗi, câu báo sai nguyên nhân


@pytest.mark.xfail(
    strict=True,
    reason="SL-T104-1: đọc lại .env ngay sau khi thay bị lỗi (file vừa bị giữ) thì câu báo nói "
    "«dòng sai định dạng… thiếu dấu nháy đóng», không đúng nguyên nhân",
)
def test_readback_failure_message_tells_the_real_cause(project_root, tmp_path, monkeypatch):
    """Bộ ghi thay ``.env`` xong thì đọc lại để kiểm. Lần đọc lại đó lỗi (ví dụ chương trình quét
    virus hay đồng bộ đang giữ file đúng lúc ấy): bộ ghi trả bản cũ (đúng, file còn nguyên), nhưng
    ``set_password`` báo «File .env có dòng sai định dạng… Mở .env, sửa dòng đó (thường là thiếu dấu
    nháy đóng)…»: người dùng đi tìm một dòng hỏng không có. Mong đợi: câu nói đúng là chưa lưu được
    vì không đọc lại được file để kiểm, file cũ còn nguyên, không nói tới dòng sai định dạng."""
    env = tmp_path / ".env"
    env.write_bytes(OTHER.encode())
    real_read = env_file._read_env_text
    calls: list[int] = []

    def flaky(path):
        calls.append(1)
        if len(calls) == 2:  # lần 1: đọc bản cũ; lần 2: đọc lại ngay sau os.replace
            raise env_file.EnvFileReadError(
                "Không đọc được file .env (PermissionError).", error_name="PermissionError"
            )
        return real_read(path)

    monkeypatch.setattr(env_file, "_read_env_text", flaky)
    code, out = run_set_password(project_root, monkeypatch, env)
    assert code == 1
    assert env.read_bytes() == OTHER.encode()  # bản cũ đã được trả lại: đúng
    assert "File .env cũ vẫn còn nguyên" in out or "file .env cũ vẫn còn nguyên" in out
    assert "sai định dạng" not in out and "dấu nháy" not in out


# =============================== SL-T104-2 (có từ trước): biến môi trường của máy đè lên .env


@pytest.mark.xfail(
    strict=True,
    reason="SL-T104-2 (có từ trước): máy có biến môi trường APP_PASSWORD_HASH thì app dùng biến "
    "đó, set_password vẫn báo «Đã lưu mật khẩu mới»: mật khẩu mới không có hiệu lực",
)
def test_os_environment_hash_is_reported(project_root, tmp_path, monkeypatch):
    """App đọc ``APP_PASSWORD_HASH`` trong biến môi trường của máy trước ``.env``
    (``load_settings``: biến môi trường đè giá trị file). Máy có biến đó (ví dụ từng đặt tay) thì
    ``set_password`` ghi ``.env`` xong báo «Đã lưu mật khẩu mới», nhưng app vẫn dùng mã băm cũ:
    mật khẩu mới bị từ chối, mật khẩu cũ vẫn đăng nhập được (như hệ quả của LC-T090-1, đường
    khác). Trang Cài đặt đã nhắc việc này cho khóa API (``overridden_by_os_environ``). Mong đợi:
    ``set_password`` báo rõ (mật khẩu mới chỉ có hiệu lực khi gỡ biến đó khỏi máy), không báo đã
    xong như bình thường."""
    env = tmp_path / ".env"
    env.write_bytes(OTHER.encode())
    monkeypatch.setenv(KEY, OLD)
    code, out = run_set_password(project_root, monkeypatch, env)
    active = load_settings(env_file=env).password_hash  # như app: biến môi trường đè .env
    assert not verify_password(NEW_PASSWORD, active)  # đúng là chưa có hiệu lực
    assert code != 0 or "biến môi trường" in out, out
