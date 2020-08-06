class ExternalServiceException(Exception):
    """Исключение при взаимодействии с внешним сервисом. """
    pass


class DatesExtractorException(Exception):
    """Исключение при извлечении даты из реплики. """
    pass


class LocationExtractorException(Exception):
    """Исключение при извлечении даты из реплики"""
    pass
