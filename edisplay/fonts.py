from enum import Enum

from PIL import ImageFont


class Fira(Enum):
    BOLD = 'Bold'
    LIGHT = 'Light'
    MEDIUM = 'Medium'
    REGULAR = 'Regular'
    RETINA = 'Retina'
    SEMIBOLD = 'SemiBold'

    @property
    def path_prefix(self):
        return 'fonts/fira-code/ttf'
    
    @property
    def font_prefix(self):
        return 'FiraCode'

    def size(self, size):
        path = f'{self.path_prefix}/{self.font_prefix}-{str(self.value)}.ttf'
        return ImageFont.truetype(path, size)


class Quicksand(Enum):
    BOLD = 'Bold'
    LIGHT = 'Light'
    MEDIUM = 'Medium'
    REGULAR = 'Regular'
    SEMIBOLD = 'SemiBold'

    @property
    def path_prefix(self):
        return 'fonts/Quicksand/static'
    
    @property
    def font_prefix(self):
        return 'Quicksand'

    def size(self, size):
        path = f'{self.path_prefix}/{self.font_prefix}-{str(self.value)}.ttf'
        return ImageFont.truetype(path, size)


class Audiowide(Enum):
    REGULAR = 'Regular'

    @property
    def path_prefix(self):
        return 'fonts/Audiowide'
    
    @property
    def font_prefix(self):
        return 'Audiowide'

    def size(self, size):
        path = f'{self.path_prefix}/{self.font_prefix}-{str(self.value)}.ttf'
        return ImageFont.truetype(path, size)
