#include "list.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

//Создает новый список и инициализирует его
list_t *list_create(size_t data_size) {
    list_t *list = malloc(sizeof(list_t));  //Выделение памяти для структуры списка
    if (!list) return NULL;               

    list->head = NULL;                     //Инициализация головы списка
    list->data_size = data_size;           //Сохранение размера данных
    return list;
}

//Проверяет пуст ли список
bool list_empty(list_t *list) {
    return list->head == NULL;             //если голова равна NULL, то true
}

//Проверяет есть ли в списке заданный элемент
bool list_contains(list_t *list, void *data) {
    list_node_t *current = list->head;     //начинает с головы
    while (current) {                     
        if (memcmp(current->data, data, list->data_size) == 0) {  //Сравнивает данные
            return true;
        }
        current = current->next;
    }
    return false;                          //Если данные не найдены
}

//Подсчитывает количество элементов в списке
size_t list_length(list_t *list) {
    size_t length = 0;
    list_node_t *current = list->head;     //Начинаем с головы
    while (current) {                      //Идем по всем узлам
        length++;
        current = current->next;
    }
    return length;                         
}

//Возвращает индекс первого вхождения элемента с заданными данными
size_t list_index(list_t *list, void *data) {
    size_t index = 0;
    list_node_t *current = list->head;     //Начинаем с головы
    while (current) {
        if (memcmp(current->data, data, list->data_size) == 0) {  //Сравниваем данные
            return index;
        }
        index++;
        current = current->next;
    }
    return SIZE_MAX;                       //возвращаем если не нашли 
}

//Удаляет и возвращает последний элемент из списка
void *list_pop(list_t *list) {
    if (!list->head) return NULL;          //Если список пуст, возвращаем NULL

    if (!list->head->next) {               //Если в списке только один узел
        void *data = list->head->data;    
        free(list->head);                  
        list->head = NULL;                 
        return data;
    }

    list_node_t *current = list->head;
    while (current->next->next) {          //Ищем предпоследний узел
        current = current->next;
    }

    void *data = current->next->data;      //Сохраняем данные последнего узла
    free(current->next);                  
    current->next = NULL;                  //Предпоследний узел теперь последний
    return data;
}

//Добавляет новый элемент в конец списка
void list_append(list_t *list, void *data) {
    list_node_t *new_node = malloc(sizeof(list_node_t));  //Создаем новый узел
    if (!new_node) return;

    new_node->data = malloc(list->data_size);             //Выделяем память под данные
    if (!new_node->data) {
        free(new_node);
        return;
    }

    memcpy(new_node->data, data, list->data_size);        //Копируем данные в новый узел
    new_node->next = NULL;

    if (!list->head) {                                    //Если список пуст
        list->head = new_node;                            //Устанавливаем новый узел как голову
        return;
    }

    list_node_t *current = list->head;                    //Ищем последний узел
    while (current->next) {
        current = current->next;
    }
    current->next = new_node;                             //Добавляем новый узел в конец
}

//Удаляет первый узел с заданным значением данных
void list_remove(list_t *list, void *data) {
    if (!list->head) return;

    if (memcmp(list->head->data, data, list->data_size) == 0) {  //Если удаляется голова
        list_node_t *temp = list->head;
        list->head = list->head->next;                  //Переподключаем голову
        free(temp->data);                               //Освобождаем память данных
        free(temp);                                     //Освобождаем память узла
        return;
    }

    list_node_t *current = list->head;
    while (current->next) {                              //Ищем узел для удаления
        if (memcmp(current->next->data, data, list->data_size) == 0) {
            list_node_t *temp = current->next;
            current->next = temp->next;                  //Переподключаем связи
            free(temp->data);                            //Освобождаем память данных
            free(temp);                                  //Освобождаем память узла
            return;
        }
        current = current->next;
    }
}

//Вставляет элемент на указанную позицию
void list_insert(list_t *list, size_t index, void *data) {
    if (!list || !data) return;

    list_node_t *new_node = malloc(sizeof(list_node_t));  //Создаем новый узел
    if (!new_node) return;

    new_node->data = malloc(list->data_size);            //Выделяем память под данные
    if (!new_node->data) {
        free(new_node);
        return;
    }

    memcpy(new_node->data, data, list->data_size);       //Копируем данные
    new_node->next = NULL;

    if (index == 0 || !list->head) {                     //Если вставка в начало
        new_node->next = list->head;
        list->head = new_node;
        return;
    }

    list_node_t *current = list->head;
    size_t current_index = 0;

    while (current->next && current_index < index - 1) { //Ищем позицию для вставки
        current = current->next;
        current_index++;
    }

    new_node->next = current->next;                      
    current->next = new_node;
}

//Удаляет список и освобождает всю выделенную память
void list_destroy(list_t *list) {
    list_node_t *current = list->head;
    while (current) {                                    //Проходим по всем узлам
        list_node_t *temp = current;
        current = current->next;
        free(temp->data);                                //Освобождаем память данных
        free(temp);                                      //Освобождаем память узла
    }
    free(list);                                         
}

//Печатает список
void list_print_int(list_t *list, FILE *stream) {
    list_node_t *current = list->head;
    while (current) {                                    //Проходим по всем узлам
        fprintf(stream, "%d -> ", *(int*)current->data); //Печатаем данные
        current = current->next;
    }
    fprintf(stream, "NULL");                             //Указываем конец списка
}


