# Báo cáo T-016 · Lưu nháp bài đang soạn (phần logic)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-016](../tickets/T-016-luu-nhap-bai-dang-soan.md) |
| Ngày nộp | 2026-10-14 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

Đã có "ngăn kéo" lưu bài đang soạn ngay trên máy (file `data/drafts.sqlite`, không đưa lên GitHub). Nó giữ đủ mọi thứ để mở lại trang Soạn bài: từ khóa, bước đang ở, chất liệu thật, kết quả nghiên cứu, dàn ý, các phần của bài kèm mọi phiên bản (nút quay lại bản trước vẫn dùng được), lần rà soát và các gợi ý đã bỏ qua. Giữ tối đa 30 nháp, tự bỏ nháp cũ nhất. Người dùng chưa thấy gì khác: giao diện tự lưu và nút Mở/Xóa là việc của Họa Sĩ ở T-017.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/storage/__init__.py` (mới) | Xuất các tên dùng chung của kho nháp. |
| `seo_app/storage/drafts.py` (mới) | Khuôn `DraftSnapshot`, `DraftPart`, `DraftSummary`; lớp `DraftStore` với `save`, `load`, `list_drafts`, `delete`. Chỉ dùng `sqlite3` và pydantic sẵn có. |
| `tests/test_storage_drafts.py` (mới) | 36 test, mọi test dùng `tmp_path`. |

Không sửa `app/`, không thêm thư viện, không chạy lệnh git làm đổi thư mục làm việc, không commit.

## Chi tiết

**Khuôn (`drafts.py:69–153`)**
- `DraftPart`: `heading`, `versions` (ít nhất 1), `current` (phải nằm trong danh sách), `image`.
- `DraftSnapshot`: `schema_version` (=1), `id` (32 ký tự hex, tự sinh), `saved_at` (bắt buộc có múi giờ), `step` (0–4), `keyword`, `material` (tối đa 20 ô), `research` (`Research`), `research_keyword`, `outline_title`, `outline` (`list[OutlineItem]`), `article_title`, `parts`, `review` (`Review`), `auto_fixed`, `ignored_flags` (nhận cả `set`, lưu thành danh sách đã sắp xếp). Thuộc tính `title`: tiêu đề bài → tiêu đề dàn ý → từ khóa → "Bài chưa đặt tên".
- `extra="forbid"`: trường lạ (ví dụ `api_key`) bị từ chối, nên không có chỗ để lỡ lưu bí mật.
- Thân bài (`versions`) được chạy lại `escape_link_syntax` khi kiểm khuôn. Hàm này idempotent nên bản đúng không đổi gì (test round-trip chứng minh), còn file bị sửa tay để chèn link Markdown thì link bị vô hiệu (`test_versions_cannot_carry_markdown_links`).

**Kho (`DraftStore`)**
- Bảng `drafts(id, title, keyword, saved_at, saved_ts, data)`; `data` là JSON của `DraftSnapshot`. Mọi câu SQL dùng `?`.
- `save`: đặt `saved_at` = giờ hiện tại theo `Asia/Ho_Chi_Minh`, kiểm khuôn lại toàn bộ, chặn nháp > 5 MB, `INSERT OR REPLACE` theo `id`, rồi xóa các nháp ngoài 30 nháp mới nhất (cùng một giao dịch).
- `load`: đo kích thước bằng SQL **trước khi** đọc dữ liệu vào bộ nhớ; quá lớn, không phải UTF-8, sai JSON, sai khuôn, mã không khớp → `DraftError` tiếng Việt. Thông báo chỉ nêu vị trí trường sai, không chép dữ liệu ra.
- `list_drafts`: trả `DraftList(drafts, skipped)`, mới nhất trước; dòng hỏng bị bỏ qua và đếm vào `skipped`.
- `delete`: trả `True`/`False`.
- File hỏng hẳn (không phải SQLite, hoặc bảng `drafts` thiếu cột): đổi tên sang `drafts.hong-YYYYMMDD-HHMMSS.sqlite` để giữ lại, tạo file mới, ghi đường dẫn vào `store.recovered_from` để giao diện báo. Lỗi khác của SQLite hoặc ổ đĩa → `DraftError` dễ hiểu ("File nháp đang bận…", "Không tạo được file nháp…").
- Mỗi thao tác mở và đóng kết nối riêng, an toàn khi Streamlit chạy nhiều luồng.

## Bằng chứng

```
$ uv run pytest
1600 passed, 3 xfailed in 72.63s (0:01:12)

$ uv run pytest tests/test_storage_drafts.py -q
36 passed in 0.58s

$ uv run ruff check .
All checks passed!
```

## Đối chiếu tiêu chí xong

- [x] Lưu, đọc lại nguyên vẹn kể cả tiếng Việt và các phiên bản: `test_save_and_load_round_trip_keeps_everything`, `test_save_overwrites_same_id`, `test_text_with_sql_and_quotes_is_stored_verbatim`
- [x] Liệt kê: `test_list_newest_first_with_title_keyword_time`
- [x] Xóa: `test_delete`
- [x] Giới hạn 30: `test_keeps_at_most_30_drafts_dropping_oldest`, `test_resaving_old_draft_moves_it_to_top_and_protects_it`
- [x] File hỏng: `test_corrupt_file_is_moved_aside_and_store_keeps_working`, `test_sqlite_with_wrong_drafts_table_is_moved_aside`, `test_unwritable_location_gives_friendly_error`
- [x] Nháp sai khuôn: `test_wrong_shape_draft_gives_friendly_error` (9 trường hợp, gồm trường lạ `api_key`, bước 99, phiên bản ngoài phạm vi, thiếu múi giờ, byte không phải UTF-8), `test_bad_rows_are_skipped_in_listing`
- [x] Nháp quá lớn: `test_too_large_draft_is_not_saved`, `test_too_large_draft_in_file_is_not_loaded`
- [x] Không `pickle`, SQL không ghép chuỗi: `test_storage_module_does_not_use_pickle_or_string_sql`, mã nháp lạ như `' OR 1=1 --` bị chặn (`test_bad_ids_are_rejected`)
- [x] `uv run pytest`, `uv run ruff check .` sạch

## Cách giao diện dùng

Dành cho Họa Sĩ (T-017). Tên khóa session lấy từ `app/views/write.py` hiện tại.

**1. Tạo kho một lần**

```python
from seo_app.storage import DraftError, DraftPart, DraftSnapshot, DraftStore, new_draft_id

@st.cache_resource
def _store_at(path: str) -> DraftStore:
    return DraftStore(Path(path))

def draft_store() -> DraftStore:
    # Đọc đường dẫn lúc chạy, để test trỏ được kho sang thư mục tạm (Soi Lỗi R8-4, sửa ở T-021).
    return _store_at(str(drafts.DEFAULT_DRAFTS_FILE))  # import seo_app.storage.drafts as drafts
```

Nếu `draft_store().recovered_from` khác `None`: báo một lần kiểu "File nháp cũ bị hỏng, đã cất sang tên khác, bắt đầu file mới".

**2. Session → nháp** (giữ nguyên chữ như trong session, không escape/unescape gì thêm)

```python
def snapshot() -> DraftSnapshot:
    return DraftSnapshot(
        id=S.setdefault("draft_id", new_draft_id()),
        step=S.step,
        keyword=S.keyword,
        material=material(),                      # các ô real-<nhãn>
        research=S.research,
        research_keyword=S.research_keyword,
        outline_title=S.outline_title,            # chưa escape, như ô sửa
        outline=[
            OutlineItem(heading=S[f"h-{u}"], points=S[f"pts-{u}"], image=S[f"img-{u}"])
            for u in S.outline_ids
        ],
        article_title=S.article_title,
        parts=[
            DraftPart(
                heading=S[f"heading-{p}"],
                versions=list(S[f"texts-{p}"]),
                current=S[f"ver-{p}"],
                image=S.get(f"img-{p}", ""),
            )
            for p in S.part_ids
        ],
        review=S.review,
        auto_fixed=S.auto_fixed,
        ignored_flags=S.ignored_flags,            # set cũng được
    )
```

Không lưu `editing-`, `manual-` (ô sửa tay chưa bấm Lưu), `style-`, `note-`, meta title/description (còn là demo).

**3. Nháp → session.** Phải chạy **trước khi vẽ widget** (giống `_start_keyword`): nút Mở dùng `on_click` đặt `S._open_draft = id`, rồi `init_state()` xử lý đầu trang.

```python
snap = draft_store().load(draft_id)   # bắt DraftError → st.error(str(exc))
reset_compose()
for key in [k for k in S if k.startswith("real-")]:   # reset_compose không xóa ô chất liệu
    del S[key]
S.draft_id = snap.id
S.keyword = snap.keyword
for label, text in snap.material.items():
    if label in MATERIAL:                  # chỉ nhận nhãn đang có
        S[f"real-{label}"] = text
S.research, S.research_keyword = snap.research, snap.research_keyword
S.outline_title = snap.outline_title     # KHÔNG unescape lần nữa (đã ở dạng ô sửa)
S.outline_ids = []
for item in snap.outline:
    uid = new_id()
    S[f"h-{uid}"], S[f"pts-{uid}"], S[f"img-{uid}"] = item.heading, list(item.points), item.image
    S.outline_ids.append(uid)
S.article_title = snap.article_title
S.part_ids = []
for part in snap.parts:
    pid = new_id()
    S[f"heading-{pid}"] = part.heading
    S[f"texts-{pid}"] = list(part.versions)
    S[f"ver-{pid}"] = part.current
    S[f"img-{pid}"] = part.image
    S.part_ids.append(pid)
S.review, S.auto_fixed = snap.review, snap.auto_fixed
S.ignored_flags = set(snap.ignored_flags)
S.step = snap.step
```

Lưu ý: `set_outline` có `unescape_link_syntax`, **đừng** dùng nó để mở nháp, vì dàn ý trong nháp đã ở dạng chưa escape.

**4. Tự lưu.** Gợi ý đơn giản và bắt được mọi kiểu thay đổi: cuối script trang, dựng `snapshot()`, so `snap.model_dump_json(exclude={"saved_at"})` với bản đã lưu lần trước (giữ trong `S._draft_saved_json`); khác thì `save`. Chỉ lưu khi đã có gì đó (`keyword()` hoặc `S.research`). Bắt `DraftError` và hiện `st.caption`/`st.warning`, không để trang sập. `save` trả bản có `saved_at` để hiện "Đã lưu lúc HH:MM": `saved.saved_at.strftime("%H:%M")`.

**5. Danh sách.** `listing = draft_store().list_drafts()`; mỗi `DraftSummary` có `id`, `title`, `keyword`, `saved_at`. Nếu `listing.skipped > 0`: báo "Có N nháp bị hỏng nên không hiện". `title` và `keyword` là chữ từ file (chưa tin cậy): hiện bằng cách không diễn giải Markdown/HTML (ví dụ nhãn nút, `st.text`, hoặc `html.escape` + `escape_link_syntax` nếu phải dùng `st.markdown`).

**6. Xóa.** `draft_store().delete(id)`; nếu xóa đúng nháp đang mở thì bỏ `S.draft_id` để lần tự lưu sau tạo nháp mới.

Mọi chữ khác từ nháp (nghiên cứu, rà soát, tiêu đề phần…) đi qua đúng các đường hiển thị sẵn có của trang, giống như khi AI vừa trả về.

## Rủi ro và điểm cần chú ý

- `research` và `review` dùng lại khuôn `Research`/`Review` của `seo_app/content`, nên khi Ngòi Bút/Thợ Máy đổi khuôn đó (thêm trường bắt buộc), nháp cũ sẽ không mở được (báo "bị hỏng"), app không sập. Khi đó nên tăng `SCHEMA_VERSION` hoặc cho trường mới giá trị mặc định.
- ~~Chữ trong `research`/`review`/`outline` lấy từ file chỉ được kiểm khuôn, không lọc lại HTML/link (trừ thân bài).~~ [Sửa ở T-021: Lá Chắn chỉ ra tiền đề này sai; nay `load` chạy lại các hàm `clean_*` cho mọi chữ do AI tạo.]
- Ai sửa được file `data/drafts.sqlite` trên máy thì cũng sửa được mã nguồn app, nên không coi đây là đường tấn công thực tế; các kiểm tra chủ yếu để file hỏng không làm sập app.
- Hai tab cùng mở một nháp và cùng sửa: bản lưu sau ghi đè bản trước (không gộp). Chấp nhận được với một người dùng.

## Đề xuất

- T-017 (Họa Sĩ): làm theo mục "Cách giao diện dùng". Có thể cân nhắc lưu thêm meta title/description khi Giai đoạn 4 làm thật (thêm trường có giá trị mặc định, không cần đổi `SCHEMA_VERSION`).
- Soi Lỗi: thêm trường hợp xấu nếu cần (file bị khóa trên Windows, đĩa đầy).

## Câu hỏi cho chủ dự án

Không có.
