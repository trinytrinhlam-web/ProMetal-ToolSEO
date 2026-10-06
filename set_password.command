#!/bin/bash
# Bấm đúp file này để đặt (hoặc đổi) mật khẩu đăng nhập SEO App.
cd "$(dirname "$0")" || exit 1
export PATH="$HOME/.local/bin:$PATH"

if ! command -v uv >/dev/null 2>&1; then
  echo "Chưa có uv. Hãy bấm đúp run.command một lần trước, sau đó chạy lại file này."
else
  uv run python scripts/hash_password.py
fi

echo
read -r -p "Nhấn Enter để đóng cửa sổ..."
