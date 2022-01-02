RESPONSE_CODES = {
    "400": (
        "Bad syntax or validation error. The request could not be understood"
        " by the API due to malformed syntax or validation errors."
    ),
    "401": "API access token missing, invalid, revoked, or expired.",
    "403.1": "The subscription for this account has lapsed.",
    "403.2": "The trial for this account has expired.",
    "403.3": (
        "The supplied access token has a scope which does not allow access."
    ),
    "403.4": (
        "The request will exceed one or more data limits in place to prevent"
        " abuse. Generally means the API request was too large for"
        " YNAB's servers to handle - try splitting the upload into smaller"
        " chunks."
    ),
    "404.1": "The specified URI does not exist.",
    "404.2": "Resource not found.",
    "409": (
        "Conflict error. If resource cannot be saved during a PUT or POST"
        " request because it conflicts with an existing resource, this error"
        " will be returned."
    ),
    "429": (
        "Too many requests, wait a while and try again. This error is returned"
        " if you make too many requests to the API in a short amount of time."
        " Please see the Rate Limiting section of the YNAB API documentation. "
    ),
    "500": (
        "Unexpected error. This error will be returned if the API experiences"
        " an unexpected error."
    ),
    "503": (
        "Service unavailable. This error will be returned if we have"
        " temporarily disabled access to the API. This can happen when we are"
        " experiencing heavy load or need to perform maintenance."
    ),
}


class YNABError(Exception):
    def __init__(self, response_code: str, detail: str):
        message = (
            f"Error {response_code} -"
            f" {RESPONSE_CODES[response_code]} ({detail.capitalize()})."
        )
        super().__init__(message)
        self.response_code = response_code
