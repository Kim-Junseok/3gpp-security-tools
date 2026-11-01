class SecurityToolsError(ValueError):
    """An error that can be presented without exposing a traceback or keys."""

    code = "INPUT_ERROR"


class UnsupportedAlgorithm(SecurityToolsError):
    code = "UNSUPPORTED_ALGORITHM"


class VectorError(SecurityToolsError):
    code = "VECTOR_UNAVAILABLE"
