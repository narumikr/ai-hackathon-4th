"""
アイコンの白背景を透過処理するスクリプト
対象: frontend/public/icons/ 内の指定アイコン（hint.png以外）

外側の白のみを透過し、内側の白は保持する（Flood Fill方式）
"""

from collections import deque
from pathlib import Path

from PIL import Image


def is_white(pixel: tuple[int, int, int, int], tolerance: int) -> bool:
    """ピクセルが白かどうか判定"""
    return pixel[0] >= 255 - tolerance and pixel[1] >= 255 - tolerance and pixel[2] >= 255 - tolerance


def remove_white_background_flood_fill(image_path: Path, tolerance: int = 30) -> None:
    """
    画像の外側の白背景のみを透過処理する（Flood Fill方式）

    Args:
        image_path: 処理対象の画像パス
        tolerance: 白と判定する許容範囲（0-255）
    """
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    pixels = img.load()

    # 透過済みのピクセルを記録
    visited = set()

    # 4方向の隣接ピクセル
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    # 画像の端から開始するピクセルを収集
    start_pixels = set()
    for x in range(width):
        start_pixels.add((x, 0))
        start_pixels.add((x, height - 1))
    for y in range(height):
        start_pixels.add((0, y))
        start_pixels.add((width - 1, y))

    # BFSで外側の白を透過
    queue = deque()
    for pos in start_pixels:
        if pos not in visited and is_white(pixels[pos], tolerance):
            queue.append(pos)
            visited.add(pos)

    while queue:
        x, y = queue.popleft()
        # 透過処理
        pixels[x, y] = (255, 255, 255, 0)

        # 隣接ピクセルをチェック
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in visited and is_white(pixels[nx, ny], tolerance):
                    visited.add((nx, ny))
                    queue.append((nx, ny))

    img.save(image_path, "PNG")
    print(f"処理完了: {image_path.name}")


def main() -> None:
    # プロジェクトルートからの相対パス
    script_dir = Path(__file__).parent
    icons_dir = script_dir.parent / "frontend" / "public" / "icons"

    # 処理対象のアイコン（hint.png以外）
    target_icons = [
        "calendar.png",
        "check.png",
        "image.png",
        "map.png",
        "museum.png",
        "note.png",
        "photo.png",
        "pin.png",
        "study.png",
        "upload.png",
        "user.png",
        "write.png",
    ]

    print(f"アイコンディレクトリ: {icons_dir}")
    print(f"処理対象: {len(target_icons)}個のアイコン\n")

    for icon_name in target_icons:
        icon_path = icons_dir / icon_name
        if icon_path.exists():
            remove_white_background_flood_fill(icon_path)
        else:
            print(f"ファイルが見つかりません: {icon_name}")

    print("\n全ての処理が完了しました")


if __name__ == "__main__":
    main()
