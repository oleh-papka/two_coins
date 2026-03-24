import random


class StylingService:
    @staticmethod
    def get_badge_bootstrap_color(color: str) -> str:
        return 'bg-warning' if random.random() < 0.5 else 'bg-success'
