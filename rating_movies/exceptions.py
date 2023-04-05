class UnavailableParameterError(Exception):
    def __init__(self, params):
        self.params = params

    def __str__(self):
        if len(self.params) == 1:
            message = f"Passed parameter '{self.params}' is unavailable"
        else:
            message = f"Passed parameters '{self.params}' are unavailable"
        return message


class AbsentParameterError(Exception):
    def __str__(self):
        return "No one parameter was passed"


class ReadFileError(Exception):
    def __init__(self, file_name):
        self.file_name = file_name

    def __str__(self):
        return f"Error reading file: '{self.file_name}'"


class WriteToFileError(Exception):
    def __init__(self, file_name):
        self.file_name = file_name

    def __str__(self):
        return f"Error writing to file: '{self.file_name}'"


class ConversionStringError(Exception):
    def __init__(self, converting_str):
        self.converting_str = converting_str

    def __str__(self):
        return f"Error converting string: '{self.converting_str}'"
