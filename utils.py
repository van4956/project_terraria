from ctypes import windll, Structure, c_long, byref

class POINT(Structure):
    '''
    Класс для хранения координат мыши.
    '''
    _fields_ = [("x", c_long), ("y", c_long)]

def queryMousePosition() -> dict:
    '''
    Получает координаты мыши.
    Возвращает словарь с координатами x и y.
    '''
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return { "x": pt.x, "y": pt.y}
