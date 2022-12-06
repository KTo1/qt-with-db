from setuptools import setup, find_packages

setup(name="monster-chat-client",
      version="1.0.0",
      description="MMMMonsterChat client application",
      author="KTo ETo",
      author_email="kto@lovetou.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
