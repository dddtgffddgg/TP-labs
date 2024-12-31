#include "list.h"

//Создает новый узел списка с заданным значением data и инициализирует его
item_t *list_create(int data) {
    item_t *item = malloc(sizeof(item_t));  //Выделение памяти для узла
    if (!item) return NULL;                
    
    item->data = data;                     //Присваивание значения узлу
    INIT_LIST_HEAD(&item->lists);          //Инициализация списка
    return item;                         
}

//Добавляет элемент с заданным значением в конец списка
void list_append(item_t *head, int data) {
    item_t *new_item = malloc(sizeof(item_t));  
    if (!new_item) return;                     
    
    new_item->data = data;                    
    INIT_LIST_HEAD(&new_item->lists);          //Инициализация списка для нового узла
    
    struct list_head *last = &head->lists;     //Указатель на голову списка
    while (last->next) {                       //Поиск последнего элемента
        last = last->next;
    }
    last->next = &new_item->lists;             //Добавление нового узла в конец
}

//Удаляет весь список и освобождает память
void list_destroy(item_t *head) {
    if (!head) return;                        
    
    struct list_head *current = &head->lists;
    while (current->next) {                    //проходит по всем узлам списка
        struct list_head *next = current->next;
        item_t *item = container_of(next, item_t, lists);  //Получение узла по структуре
        current->next = next->next;            //перемена указателей
        free(item);                        
    }
    free(head);                              
}

//Подсчитывает количество узлов в списке
size_t list_length(item_t *head) {
    if (!head) return 0;                     
    
    size_t length = 1;                        //начинает с 1
    struct list_head *current = &head->lists;  
    while (current->next) {                    //пока есть след узел
        length++;
        current = current->next;
    }
    return length;                           
}

//Проверяет содержит ли список заданное значение 
bool list_contains(item_t *head, int data) {
    if (!head) return false;                   
    
    if (head->data == data) return true;       //проверка головы
    
    struct list_head *current = &head->lists;
    while (current->next) {                    
        item_t *item = container_of(current->next, item_t, lists);
        if (item->data == data) return true;   //Если значение найдено возвращаем true
        current = current->next;
    }
    return false;                           
}

//Возвращает индекс первого узла с заданным значением
size_t list_index(item_t *head, int data) {
    if (!head) return SIZE_MAX;                
    
    if (head->data == data) return 0;          //Проверка головы
    
    size_t index = 1;
    struct list_head *current = &head->lists;
    while (current->next) {                    //Поиск по остальным узлам
        item_t *item = container_of(current->next, item_t, lists);
        if (item->data == data) return index;  //Возвращаем индекс если найдено
        current = current->next;
        index++;
    }
    return SIZE_MAX;                          
}

//Удаляет и возвращает последний элемент списка
int *list_pop(item_t *head) {
    if (!head) return NULL;                
    
    struct list_head *current = &head->lists;
    while (current->next && current->next->next) {
        current = current->next;              
    }
    
    if (!current->next) {                      //Если в списке только голова
        int *data = malloc(sizeof(int));
        if (!data) return NULL;
        *data = head->data;
        return data;
    }
    
    item_t *last = container_of(current->next, item_t, lists);  //Последний узел
    int *data = malloc(sizeof(int));
    if (!data) return NULL;
    *data = last->data;                        //Сохраняем значение последнего узла
    current->next = NULL;             
    free(last);                                //Освобождаем память
    return data;
}

//Удаляет первый найденный узел с заданным значением
void list_remove(item_t *head, int data) {
    if (!head) return;                        
    
    if (head->data == data) {                  
        if (head->lists.next) {                //Если есть следующий узел
            item_t *next_item = container_of(head->lists.next, item_t, lists);
            head->data = next_item->data;      //Перенос данных из следующего узла в голову
            head->lists.next = next_item->lists.next;
            free(next_item);                   //Удаляем следующий узел
        }
        return;
    }
    
    struct list_head *current = &head->lists;
    while (current->next) {                    //Поиск узла для удаления
        item_t *next_item = container_of(current->next, item_t, lists);
        if (next_item->data == data) {         //Если найдено
            current->next = next_item->lists.next; 
            free(next_item);                   //Удаляем узел
            return;
        }
        current = current->next;
    }
}

//Вставляет новый узел со значением на указанную позицию
void list_insert(item_t *head, size_t index, int data) {
    index++;
    if (!head) return;                     
    
    item_t *new_item = malloc(sizeof(item_t)); 
    if (!new_item) return;
    
    new_item->data = data;
    INIT_LIST_HEAD(&new_item->lists);        //Инициализация списка для нового узла
    
    if (index == 0) {                          //Если вставка в начало
        new_item->data = head->data;
        head->data = data;
        new_item->lists.next = head->lists.next;    
        head->lists.next = &new_item->lists;        //перенастраивается так, чтобы указывать на new_item
        return;
    }
    
    struct list_head *current = &head->lists;
    size_t current_index = 0;
    
    while (current->next && current_index < index - 1) {
        current = current->next;               //Поиск узла перед позицией вставки
        current_index++;
    }
    
    new_item->lists.next = current->next;      
    current->next = &new_item->lists;
}

//Печатает список в заданный поток
void list_print_int(item_t *head, FILE *stream) {
    if (!head) {                              
        fprintf(stream, "NULL");
        return;
    }
    
    fprintf(stream, "(%d)", head->data);       //Печать головы списка
    struct list_head *current = &head->lists;
    while (current->next) {                    
        item_t *item = container_of(current->next, item_t, lists);
        fprintf(stream, " -> (%d)", item->data);
        current = current->next;
    }
    fprintf(stream, " -> NULL");
}
