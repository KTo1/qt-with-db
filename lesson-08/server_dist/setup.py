from setuptools import setup, find_packages

setup(name="monster-chat-server",
      version="1.0.0",
      description="MMMMonsterChat server application",
      author="KTo ETo",
      author_email="kto@lovetou.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
      scripts=['server_app/mc_server_start']
      )
