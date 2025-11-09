__all__ = ['make_session']

import sys

from sqlalchemy.orm import sessionmaker

from .engine import SessionLocal


def make_session():
    """Создает и возвращает асинхронную сессию"""
    try:
        print("Create async transaction...")
        session = SessionLocal()
        print("Async transaction created!")
        return session
    except Exception as e:
        print(f"Couldn't create async transaction! Error: {e}")
        raise
