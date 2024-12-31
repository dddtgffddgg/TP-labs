# list_node.py

#узел односвязного списка
class ListNode:
    def __init__(self, value, next=None):       #новый узел списка
        if next is not None and not isinstance(next, ListNode):
            raise TypeError("next must be a ListNode or None")
        self.value = value      #Хранение данных узла
        self.next = next        #Ссылка на следующий узел

    def __eq__(self, other):        #Сравнивает два узла на равенство
        if not isinstance(other, ListNode):
            return False        #Если другой объект не ListNode, возвращаем False
        return self.value == other.value and self.next == other.next        #Сравнение данных и ссылок

    def __str__(self):      #Возвращает строковое представление узла
        return f"({self.value}) -> {str(self.next)}"

    def __repr__(self):     #Возвращает официальное строковое представление узла
        return self.__str__()
    
    
