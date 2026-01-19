"""振り返り集約のドメイン例外"""


class ReflectionDomainError(Exception):
    """振り返り集約のドメインエラー基底クラス"""

    pass


class ReflectionNotFoundError(ReflectionDomainError):
    """振り返りが見つからない"""

    def __init__(self, reflection_id: str):
        """ReflectionNotFoundErrorを初期化する

        Args:
            reflection_id: 見つからなかった振り返りID
        """
        self.reflection_id = reflection_id
        super().__init__(f"Reflection not found: {reflection_id}")


class InvalidReflectionError(ReflectionDomainError):
    """振り返りのバリデーションエラー"""

    pass
