"""Google Sheet giả **có trạng thái** cho test T-100: tab «KeHoach» là một lưới ô, gắn vào
``FakeGoogle`` (T-097) nên test đi qua đúng ``SheetsClient`` thật (đường cố định, ``RAW``, kiểm thân
lệnh trước khi gửi). Không gọi mạng thật (bộ chặn mạng của ``tests/conftest.py`` vẫn bật).

Gài lỗi: ``fail(tên, kết quả, apply=…)`` cho lần gọi kế tiếp của lệnh ``tên`` («read», «update»,
«append», «info», «structure») trả ``kết quả`` (mã lỗi, hay lỗi ``requests`` để client báo
``unsure``); ``apply=True``: Google đã làm xong việc rồi mới hỏng câu trả lời (mất mạng giữa chừng).
"""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import quote

from fake_google import SHEET_ID, SHEETS, FakeGoogle, json_body

from seo_app.google import sheets

INFO_URL = SHEETS + SHEET_ID
READ_URL = f"{SHEETS}{SHEET_ID}/values/{quote(sheets.READ_RANGE, safe='')}"
UPDATE_URL = f"{SHEETS}{SHEET_ID}/values:batchUpdate"
APPEND_URL = f"{SHEETS}{SHEET_ID}/values/{quote(sheets.APPEND_RANGE, safe='')}:append"
STRUCTURE_URL = f"{SHEETS}{SHEET_ID}:batchUpdate"
PLAN_ID = 777
NEW_TAB_ID = 888
_CELL = re.compile(r"'KeHoach'!([A-Z])([0-9]+)")

HEADER = [
    "Mã bài", "Từ khóa chính", "Từ khóa phụ, ý cần có", "Ý định", "Loại trang", "Ưu tiên",
    "Ngày dự kiến", "Giờ đăng", "Trạng thái", "Tiêu đề dự kiến", "Slug", "Trang dịch vụ đích",
    "Ghi chú của thợ", "Mã bài WordPress", "Ngày đăng thực tế", "Cập nhật lúc",
]  # fmt: skip


class FakePlanSheet:
    def __init__(
        self,
        fake: FakeGoogle,
        rows: list[list[Any]] | None = None,
        *,
        tabs: list[tuple[int, str]] | None = None,
    ) -> None:
        self.grid: list[list[Any]] = [list(row) for row in (rows or [])]
        self.tabs = list(tabs) if tabs is not None else [(0, "Trang tính1"), (PLAN_ID, "KeHoach")]
        self.updates: list[list[dict[str, Any]]] = []  # thân «data» của từng lệnh ghi ô
        self.update_options: list[dict[str, Any]] = []
        self.appends: list[list[Any]] = []
        self.structure: list[list[dict[str, Any]]] = []
        self.reads = 0
        self._fail: dict[str, tuple[Any, bool]] = {}
        fake.on("GET", INFO_URL, self._handler("info", self._info))
        fake.on("GET", READ_URL, self._handler("read", self._read))
        fake.on("POST", UPDATE_URL, self._handler("update", self._update))
        fake.on("POST", APPEND_URL, self._handler("append", self._append))
        fake.on("POST", STRUCTURE_URL, self._handler("structure", self._structure))

    # ---------------------------------------------------------------- gài lỗi
    def fail(self, name: str, result: Any, *, apply: bool = False) -> None:
        self._fail[name] = (result, apply)

    def _handler(self, name: str, real):
        def handle(request):
            if name in self._fail:
                result, apply = self._fail.pop(name)
                if apply:
                    real(request)
                if isinstance(result, tuple) and len(result) == 2:
                    result = (*result, {})  # (mã, thân) → (mã, thân, header) như FakeGoogle
                return result
            return real(request)

        return handle

    # ---------------------------------------------------------------- tiện cho test
    def cell(self, row: int, column: int) -> Any:
        """Ô (dòng từ 1, cột từ 0); ô chưa có là ``""``."""
        if row - 1 >= len(self.grid) or column >= len(self.grid[row - 1]):
            return ""
        return self.grid[row - 1][column]

    def set(self, row: int, column: int, value: Any) -> None:
        while len(self.grid) < row:
            self.grid.append([])
        line = self.grid[row - 1]
        while len(line) <= column:
            line.append("")
        line[column] = value

    def written_cells(self) -> list[tuple[int, int, Any]]:
        """Mọi ô đã ghi qua lệnh ghi ô: (dòng, cột, giá trị)."""
        found = []
        for data in self.updates:
            for item in data:
                match = _CELL.fullmatch(item["range"])
                found.append((int(match.group(2)), ord(match.group(1)) - 65, item["values"][0][0]))
        return found

    # ---------------------------------------------------------------- lệnh
    def _info(self, _request):
        return {
            "properties": {"title": "Kế hoạch SEO", "locale": "vi_VN", "timeZone": "Asia/Saigon"},
            "sheets": [
                {"properties": {"sheetId": sid, "title": title}} for sid, title in self.tabs
            ],
        }

    def _read(self, _request):
        self.reads += 1
        values = []
        for row in self.grid:
            trimmed = list(row)
            while trimmed and trimmed[-1] in ("", None):
                trimmed.pop()
            values.append(trimmed)
        while values and not values[-1]:
            values.pop()
        return {"range": "'KeHoach'!A1:Z1001", "majorDimension": "ROWS", "values": values}

    def _update(self, request):
        body = json_body(request)
        self.update_options.append({k: v for k, v in body.items() if k != "data"})
        self.updates.append(body["data"])
        for item in body["data"]:
            match = _CELL.fullmatch(item["range"])
            self.set(int(match.group(2)), ord(match.group(1)) - 65, item["values"][0][0])
        return {"totalUpdatedCells": len(body["data"])}

    def _append(self, request):
        body = json_body(request)
        row = body["values"][0]
        self.appends.append(row)
        last = len(self.grid)
        while last and not any(cell not in ("", None) for cell in self.grid[last - 1]):
            last -= 1
        number = last + 1
        for column, value in enumerate(row):
            self.set(number, column, value)
        return {"updates": {"updatedRange": f"'KeHoach'!A{number}:P{number}", "updatedRows": 1}}

    def _structure(self, request):
        requests_ = json_body(request)["requests"]
        self.structure.append(requests_)
        for item in requests_:
            if "addSheet" in item:
                self.tabs.append((NEW_TAB_ID, item["addSheet"]["properties"]["title"]))
        return {"spreadsheetId": SHEET_ID, "replies": [{} for _ in requests_]}


def dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)
