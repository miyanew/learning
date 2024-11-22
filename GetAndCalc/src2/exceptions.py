class AuthenticationError(Exception):
    """SFTPサーバへの認証時の例外"""

    pass


class CollectionError(Exception):
    """ファイル収集時の例外"""

    pass


class SFTPConnectionError(Exception):
    pass
