"""AIサービスのカスタム例外クラス"""


class AIServiceError(Exception):
    """AIサービスの基底例外クラス

    すべてのAIサービス関連の例外の基底クラス
    """

    pass


class AIServiceConnectionError(AIServiceError):
    """AIサービス接続エラー

    AIサービスへの接続に失敗した場合に発生する例外
    ネットワークエラー、タイムアウトなどが含まれる
    """

    pass


class AIServiceQuotaExceededError(AIServiceError):
    """AIサービスクォータ超過エラー

    APIのレート制限やクォータを超過した場合に発生する例外
    HTTP 429 Too Many Requests に対応
    """

    pass


class AIServiceInvalidRequestError(AIServiceError):
    """AIサービス不正リクエストエラー

    リクエストパラメータが不正な場合に発生する例外
    HTTP 400 Bad Request に対応
    """

    pass
