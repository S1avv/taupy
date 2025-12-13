from __future__ import annotations
from typing import List
from .var import THEME_NAMES


class TauTheme:
    """
    Represents a DaisyUI theme configuration used by TauPy.

    The class validates the requested theme name and provides access
    to the full list of supported themes. It is used internally by
    the `App` class when switching themes at runtime.
    """

    def __init__(self, theme_name: str) -> None:
        """
        Initialize a theme instance and validate its name.

        Parameters:
            theme_name (str):
                The name of the DaisyUI theme (e.g., "light", "dark", "synthwave").

        Raises:
            ValueError:
                If the provided theme name is not included in the supported theme list.
        """
        if theme_name not in THEME_NAMES:
            raise ValueError(
                f"Invalid theme name '{theme_name}'. "
                f"Available themes: {', '.join(THEME_NAMES)}"
            )

        self.theme_name: str = theme_name

    @staticmethod
    def get_all() -> List[str]:
        """
        Return a list of all supported DaisyUI themes.

        Returns:
            List[str]: A list containing all valid theme names.
        """
        return THEME_NAMES
