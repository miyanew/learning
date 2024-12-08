class SSHConfigurationError(Exception):
    """SSHコンフィグに不備あるときのエラー"""

    pass


class CollectionError(Exception):
    """ファイル収集時のエラー"""

    pass
