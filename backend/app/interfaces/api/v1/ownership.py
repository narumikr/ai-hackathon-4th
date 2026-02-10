"""リソース所有者チェックヘルパー"""

from fastapi import HTTPException, status

from app.interfaces.middleware.auth import UserContext


def verify_ownership(
    resource_user_id: str, auth: UserContext, resource_type: str = "resource"
) -> None:
    """リソースの所有者を検証する

    Args:
        resource_user_id: リソースのuser_id
        auth: 認証ユーザーコンテキスト
        resource_type: リソースタイプ（エラーメッセージ用）

    Raises:
        HTTPException: 所有者でない場合は403エラー
    """
    if resource_user_id != auth.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You do not have permission to access this {resource_type}.",
        )
