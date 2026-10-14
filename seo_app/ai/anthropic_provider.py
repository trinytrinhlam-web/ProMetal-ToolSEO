"""Gọi Claude qua thư viện chính thức ``anthropic``."""

from __future__ import annotations

from typing import Any

import anthropic

from seo_app.ai.base import AIError, T, TaskConfig, redact_secrets

# Khi Claude từ chối một yêu cầu (hiếm, do bộ lọc an toàn), máy chủ tự chạy lại bằng mô hình
# dự phòng phù hợp, không phải tự viết logic thử lại.
FALLBACK_BETA = "server-side-fallback-2026-07-01"
WEB_SEARCH_TOOL = {"type": "web_search_20260209", "name": "web_search", "max_uses": 6}
# Lượt tìm web dài có thể bị máy chủ tạm dừng (pause_turn); gửi lại để AI làm tiếp.
MAX_CONTINUATIONS = 4


class AnthropicProvider:
    def __init__(self, api_key: str, client: anthropic.Anthropic | None = None) -> None:
        self._client = client or anthropic.Anthropic(api_key=api_key, max_retries=3)

    def generate(self, task: TaskConfig, *, system: str, prompt: str, schema: type[T]) -> T:
        messages: list[dict[str, Any]] = [{"role": "user", "content": prompt}]
        extra: dict[str, Any] = {"tools": [WEB_SEARCH_TOOL]} if task.web_search else {}
        try:
            for _ in range(MAX_CONTINUATIONS + 1):
                # Dùng stream để bài dài không bị ngắt vì quá thời gian chờ.
                with self._client.beta.messages.stream(
                    model=task.model,
                    max_tokens=task.max_tokens,
                    system=system,
                    messages=messages,
                    output_format=schema,
                    output_config={"effort": task.effort},
                    betas=[FALLBACK_BETA],
                    fallbacks="default",
                    **extra,
                ) as stream:
                    message = stream.get_final_message()
                if message.stop_reason != "pause_turn":
                    break
                messages = [*messages, {"role": "assistant", "content": message.content}]
        except anthropic.AuthenticationError as exc:
            raise AIError("Khóa ANTHROPIC_API_KEY trong file .env không đúng.") from exc
        except anthropic.PermissionDeniedError as exc:
            raise AIError(f"Tài khoản Anthropic không được dùng mô hình «{task.model}».") from exc
        except anthropic.NotFoundError as exc:
            raise AIError(
                f"Không có mô hình «{task.model}». Kiểm tra lại tên trong config/ai.toml."
            ) from exc
        except anthropic.RateLimitError as exc:
            raise AIError("Anthropic đang giới hạn số lần gọi. Đợi một phút rồi thử lại.") from exc
        except anthropic.APIConnectionError as exc:
            raise AIError("Không kết nối được tới Anthropic. Kiểm tra mạng Internet.") from exc
        except anthropic.APIStatusError as exc:
            if "credit" in str(exc.message).lower():
                raise AIError("Tài khoản Anthropic đã hết tiền (credit).") from exc
            if exc.status_code == 400:
                # Thông điệp do máy chủ gửi về: che chuỗi giống khóa trước khi hiện lên màn hình.
                detail = redact_secrets(str(exc.message))
                raise AIError(f"Anthropic không nhận yêu cầu: {detail}") from exc
            raise AIError(f"Anthropic báo lỗi {exc.status_code}. Thử lại sau ít phút.") from exc
        except anthropic.APIError as exc:
            # Các lỗi còn lại của thư viện (dữ liệu trả về sai dạng…): chỉ nêu tên lỗi, không
            # chép thông điệp thô (có thể chứa header/URL).
            raise AIError(f"Lỗi khi gọi Anthropic ({type(exc).__name__}). Bấm thử lại.") from exc

        if message.stop_reason == "refusal":
            raise AIError("AI từ chối yêu cầu này. Thử diễn đạt lại từ khóa hoặc ghi chú.")
        if message.stop_reason == "max_tokens":
            raise AIError(
                f"Bài dài quá giới hạn ({task.max_tokens} token). Tăng max_tokens của việc "
                f"«{task.name}» trong config/ai.toml."
            )
        if message.stop_reason == "pause_turn":
            raise AIError("AI tìm kiếm quá lâu chưa xong. Bấm thử lại.")
        parsed = message.parsed_output
        if parsed is None:
            raise AIError("AI trả về dữ liệu không đúng khuôn. Bấm thử lại.")
        return parsed
