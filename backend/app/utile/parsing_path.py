from starlette.requests import Request


def parse_path(request: Request) -> str:
    """Парсит и нормализует путь запроса для использования в метриках StatsD.

    Извлекает шаблон пути из роута (например, /api/v1/users/{user_id})
    или использует реальный путь, если роут не найден.
    Заменяет слеши на подчеркивания для совместимости c StatsD.

    Args:
        request: Объект запроса Starlette/FastAPI.

    Returns:
        Нормализованная строка пути (например, 'api_v1_users_{user_id}').
    """
    route_path = request.scope.get("route")
    if route_path and hasattr(route_path, "path"):
        template_path = route_path.path
    else:
        template_path = request.url.path

    safe_path = template_path.replace("/", "_").strip("_")

    if not safe_path:
        safe_path = "root"

    return safe_path
