#!/bin/bash
# Bấm đúp file này để mở SEO App trên Mac.
cd "$(dirname "$0")" || exit 1

pause_and_exit() {
  echo
  read -r -p "Nhấn Enter để đóng cửa sổ..."
  exit "$1"
}

export PATH="$HOME/.local/bin:$PATH"

if ! command -v uv >/dev/null 2>&1; then
  echo "Chưa có uv trên máy. Đang cài đặt uv lần đầu, vui lòng chờ..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

if ! command -v uv >/dev/null 2>&1; then
  echo
  echo "Không cài được uv. Kiểm tra kết nối mạng rồi thử lại,"
  echo "hoặc xem mục \"Xử lý sự cố\" trong README.md."
  pause_and_exit 1
fi

echo "Đang kiểm tra và cài thư viện (lần đầu có thể mất vài phút)..."
if ! uv sync; then
  echo
  echo "Cài thư viện bị lỗi. Chụp màn hình cửa sổ này để nhờ hỗ trợ."
  pause_and_exit 1
fi

echo
echo "Đang mở SEO App trong trình duyệt..."
echo "Để TẮT app: nhấn Control + C hoặc đóng cửa sổ này."
echo
uv run streamlit run app/main.py
