from configparser import ConfigParser

def load_config(filename):
    '''
    Загружаем конфигурацию из файла
    :param filename: имя файла конфигурации
    :return: конфигурация
    '''
    parser = ConfigParser()
    parser.read(filename)

    if "bot" not in parser:
        raise ValueError("Missing [bot] section in config")

    # Преобразуем значения в int
    bot_config = {k: int(v) for k, v in parser["bot"].items()}
    return bot_config
