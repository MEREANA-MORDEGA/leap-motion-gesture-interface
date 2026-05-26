# tests/test_leap_connection.py
# -*- coding: utf-8 -*-
"""Тест подключения к Leap Motion Controller."""

import Leap
import time
import sys


class TestListener(Leap.Listener):
    """Простой слушатель для проверки работоспособности SDK."""
    
    def on_init(self, controller):
        print("✓ SDK инициализирован")
    
    def on_connect(self, controller):
        print("✓ Устройство подключено")
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)
    
    def on_frame(self, controller):
        frame = controller.frame()
        hands = frame.hands
        
        if not hands.is_empty:
            print(f"✓ Обнаружено рук: {len(hands)}")
            for hand in hands:
                print(f"  - Пальцев: {len(hand.fingers)}")
                print(f"  - Позиция ладони: {hand.palm_position}")
    
    def on_disconnect(self, controller):
        print("✗ Устройство отключено")


def main():
    listener = TestListener()
    controller = Leap.Controller()
    controller.add_listener(listener)
    
    print("Тест подключения к Leap Motion. Нажмите Ctrl+C для выхода...")
    print("Поместите руку над устройством для проверки трекинга.\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nЗавершение теста...")
        controller.remove_listener(listener)
        sys.exit(0)


if __name__ == "__main__":
    main()