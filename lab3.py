from abc import ABC, abstractmethod  
from typing import List, Any         
import random                       
import time                         


class Sorter(ABC): #базовый класс для сортировки

    def __init__(self, data: List[Any]):

        self.data = data.copy()
    
    @abstractmethod #метод сортировки
    def sort(self):

        pass

class SortObserver(Sorter): #класс для промежуточных шагов сортировки

    def __init__(self, data: List[Any]):
        
        super().__init__(data)  
        self.steps = [] #список для хранения промежуточных состояний массива
    
    def record_step(self):

        self.steps.append(self.data.copy())
    
    @abstractmethod
    def sort(self):

        pass

class CountingSort(SortObserver): #класс реализующий сортировку подсчетом

    def sort(self):

        self.record_step()  #начальное состояние массива
        if not self.data:
            return

        #минимальное и максимальное значения для создания диапазона счётчиков
        max_val = max(self.data)
        min_val = min(self.data)
        range_of_elements = max_val - min_val + 1 

        count = [0] * range_of_elements #счетчик подсчитыввает сколько раз встречается элемент в массиве

        #подсчёт количества каждого элемента в исходном массиве
        for number in self.data:
            count[number - min_val] += 1
            self.record_step()  

        #накопление счётчиков для определения позиций элементов в отсортированном массиве
        for i in range(1, len(count)):
            count[i] += count[i - 1]
            self.record_step()  

        #выходной массив для хранения отсортированных элементов
        output = [0] * len(self.data)

        #размещение элементов в правильных позициях в выходном массиве
        for number in reversed(self.data):
            output[count[number - min_val] - 1] = number
            count[number - min_val] -= 1
            self.record_step()  

        self.data = output 

class RadixSort(SortObserver): #подразрядная сортировка (радикс прямая)

    def sort(self):

        self.record_step() 
        if not self.data:
            return  

        #определение максимального числа для определения количества разрядов
        max_val = max(self.data)
        exp = 1  #текущий разряд (1 - единицы, 10 - десятки, 100 - сотни и т.д.)

        #выполнение сортировки по каждому разряду до тех пор, пока не обработаны все разряды
        while max_val // exp > 0:
            self.counting_sort(exp)  #сортировка по текущему разряду
            exp *= 10               #переход к следующему разряду

    def counting_sort(self, exp): #функция радиксной сортировки элементов с использованием сортировки подсчетом

        n = len(self.data)
        output = [0] * n  #выходной массив для хранения отсортированных элементов
        count = [0] * 10  #массив счётчиков для разрядов от 0 до 9

        #подсчёт количества элементов для текущего разряда
        for number in self.data:
            index = (number // exp) % 10  #извлекаем текущий разряд
            count[index] += 1
            self.record_step() 

        for i in range(1, 10):
            count[i] += count[i - 1]
            self.record_step() 

        #построение отсортированного массива по текущему разряду
        for number in reversed(self.data):
            index = (number // exp) % 10  #извлекаем текущий разряд
            output[count[index] - 1] = number  #размещение элемента в выходном массиве
            count[index] -= 1                
            self.record_step() #запись после размещения каждого элемента

        #обновление основного массива отсортированными данными по текущему разряду
        for i in range(n):
            self.data[i] = output[i]
            self.record_step()  #после обновления каждого элемента

def main():

    try:
        size = int(input("Введите размер массива: "))
        if size <= 0:
            print("Размер массива должен быть положительным числом.")
            return
    except ValueError:
        print("Неверный ввод. Пожалуйста, введите целое число для размера массива.")
        return
    #нижняя граница массива
    try:
        lower = int(input("Введите нижнюю границу значений: "))
    except ValueError:
        print("Неверный ввод. Пожалуйста, введите целое число для нижней границы.")
        return
    #верхняя граница массива
    try:
        upper = int(input("Введите верхнюю границу значений: "))
    except ValueError:
        print("Неверный ввод. Пожалуйста, введите целое число для верхней границы.")
        return

    if lower > upper:
        print("Нижняя граница не может быть больше верхней границы.")
        return

    #случайные числа в массиве
    data = [random.randint(lower, upper) for _ in range(size)]
    print("Исходные данные:", data)

    data_for_counting = data.copy()
    data_for_radix = data.copy()

    #сортировка подсчётом с измерением времени
    counting_sort = CountingSort(data_for_counting)
    counting_sort.sort()
    print("\nОтсортированные данные (Сортировка подсчётом):", counting_sort.data)

    #радиксная сортировка с измерением времени
    radix_sort = RadixSort(data_for_radix)
    radix_sort.sort()
    print("\nОтсортированные данные (Радиксная сортировка):", radix_sort.data)


if __name__ == "__main__":
    main()
