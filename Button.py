import pygame


class Button:
    def __init__(self, _id: int, x, y, pad_x, pad_y, text: str, font: pygame.font.Font,
                 bg: pygame.Color, bg_active: pygame.Color = None,
                 text_color: pygame.Color = None, text_color_active: pygame.Color = None,
                 outline_width: int = 0, outline_color: pygame.Color = None,
                 corner=0,
                 tag=None):

        self.id = _id
        self.x = x
        self.y = y
        self.pad_x = pad_x
        self.pad_y = pad_y
        self.bg = bg
        self.bg_active = bg_active
        self.text = text
        self.font = font
        self.text_color = text_color
        self.text_color_active = text_color_active
        self.outline_width = outline_width
        self.outline_color = outline_color
        self.corner = corner

        self.text_img = self.font.render(self.text, True, self.text_color)

        self._active = False
        self.tag = tag

    @property
    def width(self) -> int:
        return self.text_img.get_width() + (self.pad_x * 2)

    @width.setter
    def width(self, value: int):
        self.pad_x = (value - self.text_img.get_width()) // 2

    @property
    def height(self) -> int:
        return self.text_img.get_height() + (self.pad_y * 2)

    @height.setter
    def height(self, value: int):
        self.pad_y = (value - self.text_img.get_height()) // 2

    def draw(self, win):
        # outline
        if self.outline_width > 0 and self.outline_color:
            pygame.draw.rect(win, self.outline_color,
                             (self.x - self.outline_width, self.y - self.outline_width,
                              self.width + (self.outline_width * 2), self.height + (self.outline_width * 2)),
                             width=self.outline_width, border_radius=self.corner)

        pygame.draw.rect(win, self.bg_active if self._active and self.bg_active else self.bg,
                         (self.x, self.y, self.width, self.height), border_radius=self.corner)
        if self.text:
            text = self.font.render(self.text, True, self.text_color_active if self._active and self.text_color_active
                                    else self.text_color)

            win.blit(text, (
                self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    @property
    def x2(self) -> int:
        return self.x + self.width

    @x2.setter
    def x2(self, value: int):
        self.x = value - self.width

    @property
    def y2(self) -> int:
        return self.y + self.height

    @y2.setter
    def y2(self, value: int):
        self.y = value - self.height

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, value: bool):
        self._active = value

    def toggle_active(self):
        self._active = not self._active

    def is_over(self, x, y):
        return self.x < x < self.x2 and self.y < y < self.y2

    def sync_active(self, x, y):
        self._active = self.is_over(x, y)
