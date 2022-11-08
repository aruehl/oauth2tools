class OAuth2ToolsError(Exception):
    pass


class InvalidClaimValueError(OAuth2ToolsError):
    pass


class InvalidClaimTypeError(OAuth2ToolsError):
    pass


class MissingRequiredClaimError(OAuth2ToolsError):
    pass


class ParameterError(OAuth2ToolsError):
    pass


class TokenManipulationError(OAuth2ToolsError):
    pass
