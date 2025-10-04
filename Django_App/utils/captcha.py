"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-10-01 23:16:53 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
import io
import string
import random
import base64

from PIL import Image, ImageDraw, ImageFont, ImageFilter

class ImageCaptchaGenerator:
    """
    图片验证码生成器

    核心功能：生成带干扰线、噪点等干扰元素的图片验证码，支持自定义验证码长度、字符集、图片尺寸及干扰强度，
    可直接返回图片对象或保存为文件。

    Args:
        width (int): 主体图片宽度(px), recommended: at least 120px
        height (int): 主体图片高度(px), recommended: at least 40px
        font_size (int): 验证码字符大小(px), 需适配图片尺寸, recommended: at least 30px
        char_length (int, optional): 验证码字符长度(default: 4, recommended: 3-6)
        char_set (str, optional): 验证码字符集(default: 内置大小写字母集+数字集)
            - e.g. "0123456789" (仅数字)
            - e.g. "abcdef" (部分小写字母)
            - e.g. "ABC123!@#" (字母+数字+特殊符号, 适合高安全性场景)
        font_file (str, optional): 字体文件路径(.ttf或.otf格式), (default: PIL.ImageFont的默认字体)
            - e.g. "C:/Windows/Fonts/arial.ttf" 路径无效时自动回退到默认字体
        angle_range (tuple[int, int], optional): 字符旋转角度范围(default: (0, 0) 不旋转)
            - e.g. (-15, 15) 表示随机旋转 ±15°
        interference_pixel_rate (float, optional): 噪点像素占比(default: 0.0 无噪点, recommended: 0.05-0.25)
            -e.g. 0.05 (图片中 5% 的像素被渲染为噪点像素)
        interference_points (int, optional): 干扰点数量(default: 0 无干扰点, recommended: 0-20, 图片120px*40px时)
            点过多会遮挡字符, 点的长度与图片最小边正相关, 图片像素越大, 需要的点也越多
        interference_lines (int, optional): 干扰线数量(default: 0 无干扰线, recommended: 0-3 图片120px*40px时)
            线过多会遮挡字符,
        interference_circles (int, optional): 干扰圆数量(default: 0 无干扰圆, recommended: 0-3 图片120px*40px时)
            圆过多会遮挡字符, 圆的半径与图片最小边正相关, 图片像素越大, 需要的圆也越多
        output (str, optional): 验证码图片默认保存路径(default: "" 不自动保存)
            -e.g. "./captcha.png" (存到当前目录中)

    Examples:
        1. 基础配置(无干扰项)
        >>> generator = ImageCaptchaGenerator(width=120, height=40, font_size=30)
        >>> captcha_code, captcha_image = generator.generate()
        >>> captcha_map = generator.generate(10)    # 一次生成一组
        2. 上强度
        >>> generator = ImageCaptchaGenerator(
        ...    120, 40, font_size=30,
        ...    char_length=4,
        ...    font_file="./static/fonts/JetBrainsMonoNerdFontMono-Regular.ttf",
        ...    angle_range=(-60, 60),
        ...    interference_pixel_rate=0.20,
        ...    interference_points=20,
        ...    interference_lines=3,
        ...    interference_circles=2,
        ...)
        >>> captcha_code, captcha_image = generator.generate()
        3. 格式转化: 必须先.generate(count=1), 再获取不同格式的图片对象。count > 1, 暂不支持。
        >>> bytes_captcha_code = generator.bytes_image  # 图片字节流
        >>> base64_captcha_image = generator.base64_image   # 获取base64编码的字符串
        >>> image_from_base64 = generator.base64_to_image(base64_captcha_image) # base64字符串转化为图片

    """
    # 字符集 = 字母集（a~z+A~Z） + 数字集（0~9）
    _DEFAULT_CHAR_SET  = string.ascii_letters + string.digits
    _DEFAULT_WIDTH = 120
    _DEFAULT_HEIGHT = 40
    _DEFAULT_FONT_SIZE = 20
    _DEFAULT_CHAR_LENGTH = 4

    def __init__(
            self, width: int, height: int, font_size: int, *,
            char_length: int = 4,
            char_set: str = "",
            font_file: str = "",
            angle_range: tuple[int, int] = (0, 0),
            interference_pixel_rate: float = 0.0,
            interference_points: int = 0,
            interference_lines: int = 0,
            interference_circles: int = 0,
            output: str = ""
    ):
        self._width = width if width > 0 else self._DEFAULT_WIDTH
        self._height = height if height > 0 else self._DEFAULT_HEIGHT
        self._char_length = char_length if char_length > 0 else self._DEFAULT_CHAR_LENGTH
        self._font_size = font_size if font_size > 0 else self._DEFAULT_FONT_SIZE  # 字体大小
        self._font_file = font_file  # 字体文件
        # 输出选项
        self._output = output
        self._char_set = char_set or self._DEFAULT_CHAR_SET
        self._angle_range = (max(angle_range[0], -60), min(angle_range[1], 60))
        self._interference_pixel_rate = interference_pixel_rate if (0 < interference_pixel_rate < 1) else 0.0
        self._interference_points = interference_points if (interference_points > 0) else 0
        self._interference_lines = interference_lines if (interference_lines > 0) else 0
        self._interference_circles = interference_circles if (interference_circles > 0) else 0
        self._captcha_text = None
        self._captcha_map = {}
        self._font = None
        self._img = None
        self._load_font()

    def generate(self, count: int = 1):
        """
        主方法
        """
        if count == 1:
            self._draw_one()
            return self._captcha_text, self._img
        elif count > 1:
            for i in range(count):
                self._output = f"{i + 1}.jpg"
                self._draw_one()
                self._captcha_map[self._captcha_text] = self._img
            return self._captcha_map
        else:
            raise ValueError("生成数量必须大于0！")

    def _draw_one(self):
        """
        图片验证码生成器

        Returns:
            img: 包含验证码的图片对象
        """
        # 生成随机码
        self._captcha_text = self._random_captcha_text()
        # 图片对象初始化
        self._img = Image.new('RGB', (self._width, self._height), color=(255, 255, 255))
        self._draw = ImageDraw.Draw(self._img)

        char_spacing = self._width // (self._char_length + 1)  # 字符间距

        for index, char in enumerate(self._captcha_text, start=1):
            # 生成随机旋转角度
            # angle = random.randint(self._angle_range[0], self._angle_range[1])

            # 计算当前字符的绘制位置
            x = char_spacing * index  # 水平位置
            y = self._height // 2  # 垂直居中
            # 在临时图片中心绘制字符
            self._draw.text(
                (x, y),  # 临时图片的中心位置
                char,
                font=self._font,
                fill=self._random_rgb(),
                anchor="mm"  # 以中心为锚点
            )
        # 绘制干扰元素
        for i in range(int(self._width * self._height * self._interference_pixel_rate)):
            self._draw.point(xy=(random.randint(0, self._width), random.randint(0, self._height)), fill=self._random_rgb())
        self._add_interference_points(self._interference_points, int(min(self._width, self._height) * 0.08))
        self._add_interference_lines(self._interference_lines)
        self._add_interference_circles(self._interference_circles)

        # 抗锯齿
        # self._img = self._img.filter(ImageFilter.EDGE_ENHANCE_MORE)

        if self._output:
            self._img.save(self._output)

    def _load_font(self):
        # 尝试加载系统字体（若找不到则用默认字体）
        try:
            # 指定字体文件路径
            self._font = ImageFont.truetype(self._font_file, self._font_size)
        except IOError:
            # 若指定字体不存在，使用默认字体
            print("使用默认字体")
            self._font = ImageFont.load_default(self._font_size)

    def _random_captcha_text(self):
        """
        随机验证码
        """
        return "".join(random.sample(self._char_set, k=self._char_length))

    def _add_interference_points(self, count=2, point_size=2):
        """
        添加干扰点
        """
        for _ in range(count):
            # 随机点的中心坐标
            x = random.randint(point_size, self._width - point_size)
            y = random.randint(point_size, self._height - point_size)
            # 基于中心和大小计算方块的左上角和右下角坐标
            left = x - point_size // 2
            top = y - point_size // 2
            right = x + (point_size // 2 if point_size % 2 == 1 else point_size // 2)
            bottom = y + (point_size // 2 if point_size % 2 == 1 else point_size // 2)
            # 绘制实心方块
            self._draw.rectangle(
                [(left, top), (right, bottom)],
                fill=self._random_rgb()
            )

    def _add_interference_lines(self, count=2):
        """
        添加随机干扰线
        """
        for _ in range(count):
            # 随机起点和终点
            x1 = random.randint(0, self._width // 4)
            y1 = random.randint(0, self._height)
            x2 = random.randint(self._width * 3 // 4, self._width)
            y2 = random.randint(0, self._height)

            # 随机选择直线或曲线
            if random.random() < 0.5:
                # 绘制直线
                self._draw.line(
                    [(x1, y1), (x2, y2)],
                    fill=self._random_rgb(),
                    width=random.randint(1, 2)
                )
            else:
                # 贝塞尔曲线：通过中间点控制弧度：随机单中间点,让曲线更自然
                cx = random.randint(self._width // 4, self._width * 3 // 4)
                cy = random.randint(0, self._height)
                # 绘制曲线
                self._draw.line(
                    [(x1, y1), (cx, cy), (x2, y2)],
                    fill=self._random_rgb(),
                    width=random.randint(1, 2),
                    joint="curve"  # 曲线连接
                )

    def _add_interference_circles(self, count=2):
        """
        添加随机干扰圆圈
        """
        for _ in range(count):
            # 随机圆心和半径
            x = random.randint(0, self._width)
            y = random.randint(0, self._height)
            # 半径不宜过大，避免遮挡字符
            radius = random.randint(0, int(min(self._width, self._height) * 0.15))

            # 随机颜色：浅色系减少遮挡
            color = tuple(random.choices(range(150, 220), k=3))

            # 随机选择空心或实心
            if random.random() < 0.7:
                # 空心圆：随机线宽
                self._draw.ellipse(
                    [(x - radius, y - radius), (x + radius, y + radius)],
                    outline=color,
                    width=random.randint(1, 2)
                )
            else:
                # 实心圆
                self._draw.ellipse(
                    [(x - radius, y - radius), (x + radius, y + radius)],
                    fill=color
                )

    @staticmethod
    def _random_rgb():
        """
        随机 RGB 格式颜色
        """
        # 需保证人眼可识别：20以上防止过暗， 200以下防止过浅
        return tuple(random.choices(range(20, 200), k=3))

    @staticmethod
    def base64_to_image(b64_str):
        """
        将base64编码的图片字符串转为图片对象(PIL.Image)
        """
        try:
            image_bytes = base64.b64decode(b64_str)
            # 将二进制数据转换为 PIL.Image 对象
            img = Image.open(io.BytesIO(image_bytes))
            return img
        except Exception as e:
            print(f"base64转图片失败: {e}")
            return None

    @property
    def current_char_set(self):
        """
        当前使用的字符集
        """
        return self._char_set

    @property
    def captcha_text(self):
        """
        图片对应的验证码
        """
        return  self._captcha_text

    @property
    def image(self):
        """
        包含验证码的图片对象
        """
        return self._img

    @property
    def bytes_image(self):
        """
        包含验证码的图片的二进制数据流
        """
        stream = io.BytesIO()
        try:
            self._img.save(stream, format="JPEG")
            return stream.getvalue()
        except Exception as e:
            print(f"图片转二进制失败: {e}")
            return None
        finally:
            stream.close()

    @property
    def base64_image(self):
        """
        包含验证码的图片base64编码字符串
        """
        stream = io.BytesIO()
        try:
            # 将图片保存到缓冲区，方便读二进制数据
            self._img.save(stream, format='JPEG')
            # 从缓冲区读取二进制数据
            image_bytes = stream.getvalue()
            # 编码为Base64并转换为字符串
            base64_str = base64.b64encode(image_bytes).decode('utf-8')
            return base64_str
        except Exception as e:
            print(f"图片转base64失败: {e}")
            return None
        finally:
            stream.close()


if __name__ == "__main__":
    generator = ImageCaptchaGenerator(
        120, 30,
        font_size=20,
        char_length=4,
        # angle_range=(-60, 60),
        interference_pixel_rate=0.2,
        interference_points=0,
        interference_lines=2,
        interference_circles=2,
    )
    code, img = generator.generate(count=1)
    b_img = generator.bytes_image
