import os
import sys


class Colors:
    """ANSI color formatting helpers with auto-detection and graceful fallback."""

    ENABLED: bool = sys.stdout.isatty() and "NO_COLOR" not in os.environ

    RESET: str = "\033[0m" if ENABLED else ""
    BOLD: str = "\033[1m" if ENABLED else ""
    DIM: str = "\033[2m" if ENABLED else ""

    # Foreground colors
    RED: str = "\033[31m" if ENABLED else ""
    GREEN: str = "\033[32m" if ENABLED else ""
    YELLOW: str = "\033[33m" if ENABLED else ""
    BLUE: str = "\033[34m" if ENABLED else ""
    MAGENTA: str = "\033[35m" if ENABLED else ""
    CYAN: str = "\033[36m" if ENABLED else ""
    WHITE: str = "\033[37m" if ENABLED else ""

    # Bright colors
    BRIGHT_GREEN: str = "\033[92m" if ENABLED else ""
    BRIGHT_YELLOW: str = "\033[93m" if ENABLED else ""
    BRIGHT_BLUE: str = "\033[94m" if ENABLED else ""
    BRIGHT_MAGENTA: str = "\033[95m" if ENABLED else ""
    BRIGHT_CYAN: str = "\033[96m" if ENABLED else ""

    @classmethod
    def color(cls, text: str, *styles: str) -> str:
        """Wraps text in ANSI styles and resets styling."""
        if not cls.ENABLED:
            return text
        prefix = "".join(styles)
        return f"{prefix}{text}{cls.RESET}"
