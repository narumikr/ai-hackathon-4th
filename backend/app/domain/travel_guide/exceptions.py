"""TravelGuide Aggregateのドメイン例外"""


class TravelGuideDomainError(Exception):
    """TravelGuide Aggregateのドメインエラー基底クラス"""

    pass


class TravelGuideNotFoundError(TravelGuideDomainError):
    """TravelGuideが見つからない"""

    def __init__(self, guide_id: str):
        """TravelGuideNotFoundErrorを初期化する

        Args:
            guide_id: 見つからなかったガイドID
        """
        self.guide_id = guide_id
        super().__init__(f"TravelGuide not found: {guide_id}")


class InvalidTravelGuideError(TravelGuideDomainError):
    """TravelGuideのバリデーションエラー"""

    pass
