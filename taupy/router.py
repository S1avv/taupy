from __future__ import annotations
from typing import Callable, Dict, Optional, Any


class Router:
    """
    Simple path-based router for TauPy applications.

    The Router stores a mapping between route paths (e.g., "/settings")
    and handler functions responsible for rendering UI screens.

    A route handler must be a callable that returns a Component
    (either synchronously or asynchronously).

    Example:
        router = Router()
        router.register("/", home_screen)
        router.register("/settings", settings_screen)
    """

    def __init__(self) -> None:
        self.routes: Dict[str, Callable[[], Any]] = {}

    def register(self, path: str, handler: Callable[[], Any]) -> None:
        """
        Register a route handler.

        Parameters:
            path (str): Route path (e.g. "/settings").
            handler (Callable): A function returning a Component or coroutine.

        Raises:
            ValueError: If path is empty.
        """
        if not path:
            raise ValueError("Route path cannot be empty.")

        self.routes[path] = handler

    def get(self, path: str) -> Optional[Callable[[], Any]]:
        """
        Retrieve a handler by route path.

        Parameters:
            path (str): Requested route.

        Returns:
            Callable | None: The associated handler or None if not found.
        """
        return self.routes.get(path)
