# gesture_recognizer.py
# -*- coding: utf-8 -*-
"""Модуль распознавания жестов на основе данных Leap Motion."""

import logging
import numpy as np
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


class GestureRecognizer:
    """Распознаватель жестов с пороговой классификацией."""
    
    # Пороги для распознавания (настраиваемые)
    THRESHOLDS = {
        'fist': {'finger_tip_distance': 30.0},  # мм
        'swipe': {'velocity': 500.0, 'distance': 100.0},  # мм/с, мм
        'pinch': {'thumb_index_distance': 25.0},  # мм
    }
    
    def __init__(self, smoothing_alpha: float = 0.3):
        """
        Инициализация распознавателя.
        
        :param smoothing_alpha: Коэффициент экспоненциального сглаживания (0..1)
        """
        self.alpha = smoothing_alpha
        self._prev_position: Optional[np.ndarray] = None
    
    def _smooth(self, current: np.ndarray) -> np.ndarray:
        """Экспоненциальное сглаживание координат."""
        if self._prev_position is None:
            self._prev_position = current.copy()
            return current
        
        smoothed = self.alpha * current + (1 - self.alpha) * self._prev_position
        self._prev_position = smoothed.copy()
        return smoothed
    
    def _get_finger_distance(self, finger1, finger2) -> float:
        """Вычисляет расстояние между кончиками двух пальцев."""
        pos1 = np.array(finger1.tip_position)
        pos2 = np.array(finger2.tip_position)
        return np.linalg.norm(pos1 - pos2)
    
    def classify(self, hand) -> Optional[str]:
        """
        Классифицирует жест по текущему состоянию кисти.
        
        :param hand: Объект Leap.Hand из SDK
        :return: Название жеста или None
        """
        if not hand or not hand.is_valid:
            return None
        
        fingers = hand.fingers
        if len(fingers) < 5:
            return None
        
        # Получаем кончики пальцев: большой (0), указательный (1)
        thumb = fingers[0]
        index = fingers[1]
        
        # Расстояние между большим и указательным (для pinch/fist)
        tip_distance = self._get_finger_distance(thumb, index)
        
        # Проверка на кулак (все пальцы сжаты)
        if tip_distance < self.THRESHOLDS['fist']['finger_tip_distance']:
            closed_count = sum(
                self._get_finger_distance(fingers[i], fingers[i+1]) 
                < self.THRESHOLDS['fist']['finger_tip_distance']
                for i in range(4)
            )
            if closed_count >= 3:
                return 'fist'
        
        # Проверка на щипок (pinch)
        if tip_distance < self.THRESHOLDS['pinch']['thumb_index_distance']:
            return 'pinch'
        
        # Проверка на свайп (по скорости движения ладони)
        palm_pos = np.array(hand.palm_position)
        if self._prev_position is not None:
            velocity = np.linalg.norm(palm_pos - self._prev_position) * 120  # 120 FPS
            if velocity > self.THRESHOLDS['swipe']['velocity']:
                # Определяем направление
                delta = palm_pos - self._prev_position
                if abs(delta[0]) > abs(delta[1]):  # По оси X
                    return 'swipe_right' if delta[0] > 0 else 'swipe_left'
                else:  # По оси Y
                    return 'swipe_up' if delta[1] > 0 else 'swipe_down'
        
        # Сглаживание позиции для следующего кадра
        self._smooth(palm_pos)
        
        return None