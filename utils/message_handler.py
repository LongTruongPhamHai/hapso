import pygame
from typing import Optional


class MessageHandler:
    def __init__(self, duration_ms: int = 3000):
        self.message: str = ""
        self.message_time: int = 0
        self.duration_ms = duration_ms

    def set_message(self, message: str) -> None:
        self.message = message
        self.message_time = pygame.time.get_ticks()

    def is_message_active(self) -> bool:
        if not self.message:
            return False
        current_time = pygame.time.get_ticks()
        return current_time - self.message_time < self.duration_ms

    def clear_message(self) -> None:
        self.message = ""
        self.message_time = 0

    def get_message(self) -> Optional[str]:
        if self.is_message_active():
            return self.message
        return None
