# context_manager.py
# -*- coding: utf-8 -*-
"""Менеджер контекста: детекция активного окна и загрузка профилей."""

import yaml
import psutil
import logging
from pathlib import Path
from typing import Optional, Dict

# Настройка логирования
logger = logging.getLogger(__name__)

try:
    import win32gui
    import win32process
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
    logger.warning("Модули win32 не найдены. Детекция окон отключена.")


class ContextManager:
    """Менеджер контекста для динамического переключения профилей жестов."""
    
    def __init__(self, profiles_dir: str = "config/profiles"):
        self.profiles_dir = Path(profiles_dir)
        self.current_profile: Optional[Dict] = None
        self._cache: Dict[str, Dict] = {}
        self._last_app: Optional[str] = None
        
        if not self.profiles_dir.exists():
            self.profiles_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Создана директория профилей: {self.profiles_dir}")
    
    def get_active_app(self) -> Optional[str]:
        """Возвращает имя исполняемого файла активного окна (Windows)."""
        if not WINDOWS_AVAILABLE:
            return None
            
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return None
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            proc = psutil.Process(pid)
            return proc.name().lower()
        except (psutil.NoSuchProcess, psutil.AccessDenied, OSError) as e:
            logger.debug(f"Не удалось получить активное приложение: {e}")
            return None
    
    def load_profile(self, app_name: str) -> Optional[Dict]:
        """Загружает профиль для приложения из YAML-файла."""
        if not app_name:
            return None
            
        if app_name in self._cache:
            return self._cache[app_name]
        
        try:
            for profile_file in self.profiles_dir.glob("*.yaml"):
                with open(profile_file, "r", encoding="utf-8") as f:
                    profile = yaml.safe_load(f)
                    if not isinstance(profile, dict):
                        continue
                    app_match = profile.get("app_match", [])
                    if isinstance(app_match, list) and app_name in app_match:
                        self._cache[app_name] = profile
                        logger.info(f"Загружен профиль для {app_name}")
                        return profile
        except (yaml.YAMLError, IOError) as e:
            logger.error(f"Ошибка загрузки профиля: {e}")
        
        return None
    
    def update_context(self) -> bool:
        """Обновляет контекст: при смене приложения загружает новый профиль."""
        app = self.get_active_app()
        if app and app != self._last_app:
            profile = self.load_profile(app)
            if profile:
                self.current_profile = profile
                self._last_app = app
                return True
            else:
                logger.debug(f"Профиль для {app} не найден, используется профиль по умолчанию")
        return False
    
    def get_gesture_config(self, gesture_name: str) -> Optional[Dict]:
        """Возвращает конфигурацию конкретного жеста из текущего профиля."""
        if not self.current_profile:
            return None
        gestures = self.current_profile.get("gestures", {})
        return gestures.get(gesture_name)