class ListNode:
    def __init__(self, *args):
        self.value = args[0]
        self.next = None

        if len(args) > 1:
            if isinstance(args[1], ListNode):
                self.next = args[1]
            else: 
                raise TypeError()  

    def __str__(self):
        return f"({self.value}) -> {self.next}"
        
        #(1) -> (2) -> (3) -> None
        #a = ListNode(5)
        #ListNode(6, a)
        #a = ListNode(3)
        #b = ListNode(2, a)
        #c = ListNode(1, b)
            
        #print(str(c))

    def __eq__(self, node2):
            if isinstance(self, ListNode):
                isinstance(node2, ListNode)
                if (self.value == node2.value) and (self.next == node2.next):
                    return True
            return False

    def __ne__(self, node2):
            #if isinstance(self, ListNode):
            #    isinstance(node2, ListNode)
            #    if (self.value != node2.value) or (self.next != node2.next):
            #        return True
            #return False
        return not (self == node2)
a= ListNode(3) 
b= ListNode(4)
print(a != b)





