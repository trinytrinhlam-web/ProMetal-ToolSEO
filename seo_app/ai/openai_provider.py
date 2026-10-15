"""Gọi ChatGPT qua thư viện chính thức ``openai`` (Responses API).

Quy đổi ``effort`` của app sang ``reasoning.effort`` của OpenAI (cùng tên, không phải đổi):

=========  ==========================
app        OpenAI ``reasoning.effort``
=========  ==========================
low        low
medium     medium
high       high
xhigh      xhigh
max        max
=========  ==========================

Mô hình không suy nghĩ (ví dụ ``gpt-4.1``) hoặc không nhận mức đã chọn thì máy chủ báo lỗi 400
về ``reasoning``; khi đó gọi lại đúng một lần **không** kèm ``reasoning`` (bỏ qua, không lỗi).

Tìm web: công cụ ``web_search`` chính hãng dùng được cùng lúc với kết quả có khuôn
(``text.format = json_schema``), nên chỉ cần một lượt gọi.
"""

from __future__ import annotations

from typing import Any

import openai
import pydantic

from seo_app.ai.base import AIError, T, TaskConfig, redact_secrets

# Tìm web như người dùng ở Việt Nam (kết quả Google Việt Nam sát hơn).
WEB_SEARCH_TOOL = {
    "type": "web_search",
    "user_location": {"type": "approximate", "country": "VN", "timezone": "Asia/Ho_Chi_Minh"},
}
# Bài dài, suy nghĩ kỹ và tìm web có thể mất vài phút; quá 15 phút thì dừng.
TIMEOUT_SECONDS = 900.0


class OpenAIProvider:
    def __init__(self, api_key: str, client: openai.OpenAI | None = None) -> None:
        self._client = client or openai.OpenAI(
            api_key=api_key, timeout=TIMEOUT_SECONDS, max_retries=3
        )

    def generate(self, task: TaskConfig, *, system: str, prompt: str, schema: type[T]) -> T:
        params: dict[str, Any] = {
            "model": task.model,
            "instructions": system,
            "input": prompt,
            "max_output_tokens": task.max_tokens,
            "text": {"format": text_format(schema)},
            "reasoning": {"effort": task.effort},
            # Không lưu bài trên máy chủ OpenAI (mỗi lượt gọi đã đủ dữ liệu).
            "store": False,
        }
        # AI chỉ có đúng một công cụ là tìm web, và chỉ ở việc được bật web_search (security A2).
        if task.web_search:
            params["tools"] = [WEB_SEARCH_TOOL]
        try:
            try:
                response = self._client.responses.create(**params)
            except openai.BadRequestError as exc:
                if not _about_reasoning(exc):
                    raise
                # Mô hình không suy nghĩ / không nhận mức effort này: bỏ qua, gọi lại một lần.
                params.pop("reasoning")
                response = self._client.responses.create(**params)
        except openai.AuthenticationError as exc:
            raise AIError("Khóa OPENAI_API_KEY trong file .env không đúng.") from exc
        except openai.PermissionDeniedError as exc:
            raise AIError(f"Tài khoản OpenAI không được dùng mô hình «{task.model}».") from exc
        except openai.NotFoundError as exc:
            raise AIError(
                f"Không có mô hình «{task.model}». Kiểm tra lại tên trong config/ai.toml."
            ) from exc
        except openai.RateLimitError as exc:
            if exc.code == "insufficient_quota":
                raise AIError("Tài khoản OpenAI đã hết tiền (credit) hoặc hết hạn mức.") from exc
            raise AIError("OpenAI đang giới hạn số lần gọi. Đợi một phút rồi thử lại.") from exc
        except openai.APITimeoutError as exc:
            raise AIError("OpenAI trả lời quá lâu. Bấm thử lại.") from exc
        except openai.APIConnectionError as exc:
            raise AIError("Không kết nối được tới OpenAI. Kiểm tra mạng Internet.") from exc
        except openai.APIStatusError as exc:
            if exc.status_code == 400:
                # Thông điệp do máy chủ gửi về: che chuỗi giống khóa trước khi hiện lên màn hình.
                detail = redact_secrets(str(exc.message))
                raise AIError(f"OpenAI không nhận yêu cầu: {detail}") from exc
            raise AIError(f"OpenAI báo lỗi {exc.status_code}. Thử lại sau ít phút.") from exc
        except openai.OpenAIError as exc:
            # Các lỗi còn lại của thư viện: chỉ nêu tên lỗi, không chép thông điệp thô.
            raise AIError(f"Lỗi khi gọi OpenAI ({type(exc).__name__}). Bấm thử lại.") from exc

        return _parse(response, task, schema)


def text_format(schema: type[T]) -> dict[str, Any]:
    """Khuôn ``json_schema`` (strict) cho Responses API, dựng bằng hàm công khai của thư viện.

    ``openai.pydantic_function_tool`` đổi lớp pydantic sang JSON Schema "strict" đúng như
    ``responses.parse`` làm, nhưng không đụng tới hàm nội bộ (``openai.lib._parsing``) có thể
    đổi tên giữa các phiên bản.
    """
    function = openai.pydantic_function_tool(schema)["function"]
    return {
        "type": "json_schema",
        "name": function["name"],
        "strict": True,
        "schema": function["parameters"],
    }


def _about_reasoning(exc: openai.BadRequestError) -> bool:
    """Lỗi 400 vì tham số ``reasoning`` (mô hình không suy nghĩ hoặc không nhận mức này)."""
    param = str(getattr(exc, "param", None) or "").lower()
    return param.startswith("reasoning") or "reasoning" in str(exc.message).lower()


def _parse(response: Any, task: TaskConfig, schema: type[T]) -> T:
    """Kiểm tra trạng thái rồi đối chiếu câu trả lời với khuôn ``schema``."""
    status = getattr(response, "status", None)
    reason = getattr(getattr(response, "incomplete_details", None), "reason", None)
    if status == "incomplete" and reason == "max_output_tokens":
        raise AIError(
            f"Bài dài quá giới hạn ({task.max_tokens} token). Tăng max_tokens của việc "
            f"«{task.name}» trong config/ai.toml."
        )
    if status == "incomplete" and reason == "content_filter":
        raise AIError("AI từ chối yêu cầu này. Thử diễn đạt lại từ khóa hoặc ghi chú.")
    if status in ("failed", "cancelled", "incomplete"):
        raise AIError("OpenAI chưa trả lời xong. Bấm thử lại.")

    texts: list[str] = []
    for item in getattr(response, "output", None) or []:
        if getattr(item, "type", None) != "message":
            continue
        # Chỉ lấy câu trả lời cuối (bỏ các đoạn "đang làm" nếu mô hình có gửi kèm).
        if getattr(item, "phase", None) not in (None, "final_answer"):
            continue
        for content in getattr(item, "content", None) or []:
            kind = getattr(content, "type", None)
            if kind == "refusal":
                raise AIError("AI từ chối yêu cầu này. Thử diễn đạt lại từ khóa hoặc ghi chú.")
            if kind == "output_text" and getattr(content, "text", None):
                texts.append(content.text)
    if not texts:
        raise AIError("AI trả về dữ liệu không đúng khuôn. Bấm thử lại.")
    try:
        return schema.model_validate_json(texts[-1])
    except pydantic.ValidationError as exc:
        raise AIError("AI trả về dữ liệu không đúng khuôn. Bấm thử lại.") from exc
