from src.logger import Logger


def main() -> None:
    """Main function to run the application."""
    logs = Logger(name="application", file_logging=False)
    logs.info("Hello, world!")


if __name__ == "__main__":
    main()
