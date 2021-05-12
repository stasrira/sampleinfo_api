from .error import Error


class EntityErrors:
    entity = None  # link to an object that these errors belongs to.

    def __init__(self, new_entity):
        self.entity = new_entity
        self.__errors = []

    def add_error(self, error_desc, error_number=None, send_email=None):
        error = Error(error_desc, error_number)
        self.__errors.append(error)
        if send_email:
            self.send_email(error_desc, error_number)

    def exist(self):
        if self.__errors:
            return len(self.__errors) > 0
        else:
            return False

    @property
    def count(self):
        if self.__errors:
            return len(self.__errors)
        else:
            return 0

    def get_errors(self):
        return self.__errors

    @property
    def errors(self):
        return self.__errors

    def send_email(self, error_desc, error_number):
        pass