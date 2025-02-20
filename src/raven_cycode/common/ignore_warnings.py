import warnings


def ignore_warnings():
    # Ignore urllib3 warning about OpenSSL version
    warnings.filterwarnings(
        "ignore",
        module="urllib3",
        message="urllib3 v2.0 only supports OpenSSL 1.1.1+.*",
    )
