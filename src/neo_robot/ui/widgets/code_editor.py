"""Code editor widget for the student coding environment."""

from __future__ import annotations

from textual.widgets import TextArea


_DEFAULT_CODE = """\
# Viết mã Python của bạn ở đây!
# Dùng 'arm' để điều khiển robot:
#
#   arm.turn_left(90)   - xoay tay trái
#   arm.turn_right(45)  - xoay tay phải
#   arm.grab()          - kẹp lại
#   arm.release()       - mở kẹp
#   delay(seconds)      - đợi trước lệnh tiếp theo
#
# Ví dụ: gắp một vật
#   arm.turn_right(90)
#   delay(1)
#   arm.grab()
#   arm.turn_left(90)
#   arm.release()

"""


class CodeEditor(TextArea):
    """Python code editor with syntax highlighting and line numbers.

    Built on top of Textual's :class:`~textual.widgets.TextArea` which
    provides syntax highlighting via *tree-sitter*, line numbers, and
    keyboard-driven editing out of the box.
    """

    def __init__(self, **kwargs) -> None:  # type: ignore[override]
        super().__init__(
            _DEFAULT_CODE,
            language="python",
            theme="monokai",
            show_line_numbers=True,
            tab_behavior="indent",
            **kwargs,
        )

    # -- public helpers ------------------------------------------------

    def get_code(self) -> str:
        """Return the current editor contents as a string."""
        return self.text

    def set_code(self, code: str) -> None:
        """Replace the editor contents with *code*."""
        self.load_text(code)
