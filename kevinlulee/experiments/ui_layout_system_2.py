


        
    def set_position(self, x, y):
        self.frame.origin.x = x
        self.frame.origin.y = y
        
    def set_size(self, width, height):
        self.frame.width = width
        self.frame.height = height



def elt(x = 0, y = 0, width = 1, height = 1, id = None):
    el = Element()
    el.frame.width = width
    el.frame.height = height
    el.frame.origin.x = x
    el.frame.origin.y = y
    return el

el = Element(id = "sam")
