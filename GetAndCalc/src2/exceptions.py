class AuthenticationError(Exception):
    """SFTPサーバへの認証時のエラー"""

    pass


class CollectionError(Exception):
    """ファイル収集時のエラー"""

    pass


class FileWriteError(Exception):
    """ファイル書込み時のエラー"""

    pass
