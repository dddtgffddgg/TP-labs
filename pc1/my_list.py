from list_node import ListNode

#односвязный список
class MyList:
    def __init__(self, value=None):
        self.head = ListNode(value) if value is not None else None
        self._length = 1 if value is not None else 0 #количество элементов в списке

    #добавление элемента в конец списка
    def append(self, value):
        new_node = ListNode(value)  #создание нового узла
        if not self.head: 
            self.head = new_node  #если список пуст,новый узел становится головой
        else:
            current = self.head 
            while current.next:
                current = current.next
            current.next = new_node  #присоединяет новый узел к последнему
        self._length += 1

    #возвращает количество элементов в списке
    def __len__(self):
        return self._length

    def __str__(self):  #строковое представление каждого узла
        if not self.head:
            return "None"
        return str(self.head)

    def __repr__(self):     #Возвращает строковое представление списка для отладки
        return self.__str__()

    def __eq__(self, other): #сравнение двух списков
        if not isinstance(other, MyList):
            return False
        return self.head == other.head  #Сравнивает узлы двух списков

    def __contains__(self, value): #проверяет, есть ли значение в списке
        current = self.head
        while current:
            if current.value == value:
                return True
            current = current.next
        return False

    def remove(self, value):  #Удаляет первое вхождение
        if not self.head:
            raise ValueError("List is empty")

        if self.head.value == value:
            self.head = self.head.next  #если знач в голове то удаляет голову списка
            self._length -= 1
            return

        current = self.head
        while current.next:
            if current.next.value == value: #Сравнивается значение
                current.next = current.next.next #удаление узла из списка
                self._length -= 1
                return
            current = current.next
        raise ValueError("Value not found in list")

    def pop(self):  #удаление последнего элемента из списка и возвращает его знач
        if not self.head:
            raise IndexError("pop from empty list")

        if not self.head.next:      #если в списке только один элемент
            value = self.head.value
            self.head = None  #удаляет голову,список пустой
            self._length = 0
            return value

        current = self.head
        while current.next.next:
            current = current.next  #переходим к след узлу
        value = current.next.value
        current.next = None  #Удаление последнего узла
        self._length -= 1
        return value

    def clear(self): # Очищение списка
        self.head = None
        self._length = 0

    def extend(self, other): #Расширяет текущий список элементами другого списка
        if not isinstance(other, MyList):
            raise TypeError("can only extend with MyList")

        if not other.head:
            return  #Если другой список пуст

        if not self.head:       #Если текущий список пуст
            self.head = ListNode(other.head.value)  #Если текущий список пуст cоздает новый узел из головы другого списка
            current_self = self.head
            current_other = other.head.next
        else:
            current_self = self.head
            while current_self.next:  
                current_self = current_self.next  #Поиск последнего узла текущего списка
            current_other = other.head

        while current_other:
            current_self.next = ListNode(current_other.value)   #Добавление нового узла с данными другого списка
            current_self = current_self.next
            current_other = current_other.next
        self._length += len(other)

    def copy(self):  #Создает копию текущего списка
        new_list = MyList()
        if not self.head:
            return new_list #Возвращаем пустой список

        new_list.head = ListNode(self.head.value)  #Копирование головы
        current_new = new_list.head
        current = self.head.next

        while current:
            current_new.next = ListNode(current.value) #Копирование узлов
            current_new = current_new.next
            current = current.next

        new_list._length = self._length  # Установка длины копии
        return new_list

    def insert(self, index, value):  #Вставляет элемент в список на заданную позицию
        if not isinstance(index, int):
            raise IndexError("Index must be an integer") #Если индекс не является целым числом
        if index < 0:
            raise IndexError("Index out of range") #Если индекс вне допустимого диапазона

        if index == 0:
            new_node = ListNode(value)
            new_node.next = self.head  # Вставка в начало списка
            self.head = new_node
            self._length += 1   
            return

        if index >= self._length:
            self.append(value)  #Вставка в конец списка
            return

        current = self.head
        position = 0
        while current and position < index - 1:
            current = current.next
            position += 1

        new_node = ListNode(value)
        new_node.next = current.next
        current.next = new_node
        self._length += 1

    def reverse(self): #Разворачивает список
        if not self.head or not self.head.next:
            return

        prev = None
        current = self.head
        while current:
            next_node = current.next #Сохранение ссылки на следующий узел
            current.next = prev         #Переворот ссылки
            prev = current              #Перемещение предыдущего узла
            current = next_node         #Перемещение текущего узла
        self.head = prev            #Обновление головы списка

    def index(self, value):         #Возвращает индекс первого вхождения элемента
        if not self.head:
            raise ValueError("Value not found in list")

        current = self.head
        index = 0
        while current:
            if current.value == value:
                return index
            current = current.next
            index += 1
        raise ValueError("Value not found in list")

    def count(self, value):     #Считает, сколько раз элемент встречается в списке
        count = 0
        current = self.head
        while current:
            if current.value == value:
                count += 1
            current = current.next
        return count
