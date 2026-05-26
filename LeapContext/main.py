# main.py
# -*- coding: utf-8 -*-
"""Точка входа в модуль LeapContext."""

import Leap
import time
import logging
import sys
from context_manager import ContextManager
from gesture_recognizer import GestureRecognizer
from command_dispatcher import CommandDispatcher

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('leap_context.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class LeapContextApp:
    """Основной класс приложения."""
    
    def __init__(self):
        self.context_manager = ContextManager()
        self.gesture_recognizer = GestureRecognizer()
        self.command_dispatcher = CommandDispatcher()
        self.running = False
    
    def on_frame(self, controller):
        """Обработчик каждого кадра от Leap Motion."""
        frame = controller.frame()
        
        # Обновление контекста (активное окно)
        if self.context_manager.update_context():
            profile_name = self.context_manager.current_profile.get('ui_feedback', {}).get('profile_name', 'Default')
            logger.info(f"Смена профиля: {profile_name}")
        
        # Обработка рук
        for hand in frame.hands:
            if not hand.is_valid:
                continue
            
            # Распознавание жеста
            gesture = self.gesture_recognizer.classify(hand)
            if gesture:
                logger.debug(f"Распознан жест: {gesture}")
                
                # Получение конфигурации жеста из профиля
                config = self.context_manager.get_gesture_config(gesture)
                if config:
                    # Выполнение команды
                    success = self.command_dispatcher.execute(config)
                    if success:
                        logger.info(f"Команда выполнена: {config.get('action')}")
    
    def run(self):
        """Запуск основного цикла приложения."""
        logger.info("Запуск LeapContext...")
        
        controller = Leap.Controller()
        controller.add_listener(self)  # Сам объект как слушатель
        
        self.running = True
        logger.info("Ожидание данных от Leap Motion...")
        
        try:
            while self.running:
                time.sleep(0.01)  # Минимальная загрузка ЦП
        except KeyboardInterrupt:
            logger.info("Получен сигнал завершения")
        finally:
            controller.remove_listener(self)
            logger.info("Приложение завершено")
    
    def stop(self):
        """Остановка приложения."""
        self.running = False


def main():
    """Точка входа в скрипт."""
    app = LeapContextApp()
    app.run()


if __name__ == "__main__":
    main()