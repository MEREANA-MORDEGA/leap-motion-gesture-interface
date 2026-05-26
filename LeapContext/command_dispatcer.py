# command_dispatcher.py
# -*- coding: utf-8 -*-
"""Модуль выполнения команд на основе распознанных жестов."""

import logging
import platform
from typing import Dict, Optional

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logging.warning("pyautogui не установлен. Эмуляция ввода отключена.")

logger = logging.getLogger(__name__)


class CommandDispatcher:
    """Диспетчер команд: преобразует конфигурацию жеста в действие."""
    
    def __init__(self, dry_run: bool = False):
        """
        :param dry_run: Если True, команды не выполняются, только логируются
        """
        self.dry_run = dry_run
        if PYAUTOGUI_AVAILABLE and not dry_run:
            pyautogui.FAILSAFE = True  # Безопасность: перемещение в угол экрана останавливает скрипт
    
    def execute(self, config: Dict) -> bool:
        """
        Выполняет команду на основе конфигурации.
        
        :param config: Словарь конфигурации жеста из YAML
        :return: True, если команда выполнена успешно
        """
        action = config.get('action')
        params = config.get('params', {})
        
        if not action:
            logger.warning("Пустое действие в конфигурации")
            return False
        
        logger.info(f"Выполнение действия: {action}, параметры: {params}")
        
        if self.dry_run:
            return True
        
        try:
            if action == 'next_tab':
                return self._press_hotkey(params.get('modifier'), params.get('key'))
            elif action == 'prev_tab':
                return self._press_hotkey(params.get('modifier'), params.get('key'), count=-1)
            elif action == 'volume_up':
                return self._adjust_volume(params.get('step', 5))
            elif action == 'volume_down':
                return self._adjust_volume(-params.get('step', 5))
            elif action == 'play_pause':
                return self._press_media_key('play_pause')
            elif action == 'zoom_in':
                return self._zoom(params.get('step', 0.1))
            else:
                logger.warning(f"Неизвестное действие: {action}")
                return False
        except Exception as e:
            logger.error(f"Ошибка выполнения команды: {e}")
            return False
    
    def _press_hotkey(self, modifier: Optional[str], key: Optional[str], count: int = 1) -> bool:
        """Нажимает комбинацию клавиш с модификатором."""
        if not PYAUTOGUI_AVAILABLE or not modifier or not key:
            return False
        
        for _ in range(abs(count)):
            if modifier.lower() == 'ctrl':
                pyautogui.hotkey('ctrl', key)
            elif modifier.lower() == 'alt':
                pyautogui.hotkey('alt', key)
            elif modifier.lower() == 'shift':
                pyautogui.hotkey('shift', key)
        return True
    
    def _adjust_volume(self, step: int) -> bool:
        """Изменяет громкость системы."""
        if not PYAUTOGUI_AVAILABLE:
            return False
        
        # Эмуляция нажатия клавиш громкости
        key = 'volumeup' if step > 0 else 'volumedown'
        for _ in range(abs(step)):
            pyautogui.press(key)
        return True
    
    def _press_media_key(self, key: str) -> bool:
        """Нажимает медиа-клавишу."""
        if not PYAUTOGUI_AVAILABLE:
            return False
        
        pyautogui.press(key)
        return True
    
    def _zoom(self, step: float) -> bool:
        """Эмулирует зум через Ctrl+колесо мыши."""
        if not PYAUTOGUI_AVAILABLE:
            return False
        
        clicks = int(step * 10)  # Масштабирование шага
        if clicks > 0:
            pyautogui.hotkey('ctrl', 'plus')
        else:
            pyautogui.hotkey('ctrl', 'minus')
        return True