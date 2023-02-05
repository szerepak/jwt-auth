import dotenv


def load_config() -> dict[str, str | None]:
    return dotenv.dotenv_values(".env")
