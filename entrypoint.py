import logging

from app.app import App

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

if __name__ == "__main__":
    app = App()
    app.run()
