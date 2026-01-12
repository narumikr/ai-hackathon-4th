"""Reflection Aggregateのドメイン例外"""


class ReflectionDomainError(Exception):
    """Reflection Aggregateのドメインエラー基底クラス"""

    pass


class ReflectionNotFoundError(ReflectionDomainError):
    """Reflectionが見つからない"""

    def __init__(self, reflection_id: str):
        """ReflectionNotFoundErrorを初期化する

        Args:
            reflection_id: 見つからなかった振り返りID
        """
        self.reflection_id = reflection_id
        super().__init__(f"Reflection not found: {reflection_id}")


class InvalidReflectionError(ReflectionDomainError):
    """Reflectionのバリデーションエラー"""

    pass
