import requests
import time

#список имён, которые будем искать в тексте
MAIN_CHARACTERS = [
    "Пьер",    
    "Андрей",  
    "Наташа",  
    "Марья",   
    "Николай"  
]

#ссылка на текст "Войны и мира"
URL = "https://evil-teacher.on.fleek.co/tp/war_and_peace.txt"

# функции для наивного (прямого) поиска
def naive_search(text: str, pattern: str):

    #наивный алгоритм поиска всех вхождений паттерна в тексте.
    #возвращает список индексов, с которых начинаются совпадения.

    occurrences = []
    plen = len(pattern)
    tlen = len(text)

    for i in range(tlen - plen + 1):
        #проверяем, совпадает ли подстрока с pattern
        if text[i:i+plen] == pattern:
            occurrences.append(i)
    return occurrences

#функции для КМП (Knuth–Morris–Pratt) поиска
def compute_lps(pattern: str):

    #вычисляет массив "longest prefix suffix" (LPS) для паттерна.
    #LPS[i] — это длина наибольшего суффикса подстроки,
    #который одновременно является её префиксом.
    
    lps = [0] * len(pattern)
    prefix_end = 0  #длина текущего совпавшего префикса
    i = 1

    while i < len(pattern):
        if pattern[i] == pattern[prefix_end]:
            prefix_end += 1
            lps[i] = prefix_end
            i += 1
        else:
            if prefix_end != 0:
                prefix_end = lps[prefix_end - 1]
            else:
                lps[i] = 0
                i += 1

    return lps

def kmp_search(text: str, pattern: str):
    
    #алгоритм Кнута–Морриса–Пратта. ищет все вхождения 'pattern' в 'text'.
    #возвращает список индексов вхождений.
    
    lps = compute_lps(pattern)
    occurrences = []

    t_i = 0  #индекс в тексте
    p_i = 0  #индекс в паттерне
    while t_i < len(text):
        if text[t_i] == pattern[p_i]:
            t_i += 1
            p_i += 1

            #если мы дошли до конца паттерна, значит нашли вхождение
            if p_i == len(pattern):
                occurrences.append(t_i - p_i)
                #продолжаем поиск
                p_i = lps[p_i - 1]
        else:
            #если символы не совпали
            if p_i != 0:
                p_i = lps[p_i - 1]
            else:
                t_i += 1

    return occurrences

#основная программа
def main():
    print("Текст 'Война и мир'...")
    response = requests.get(URL)
    text = response.text
    print("Текст успешно загружен.")


    total_occurrences_naive = 0
    total_occurrences_kmp = 0

    naive_time_stats = {}
    kmp_time_stats = {}

    for name in MAIN_CHARACTERS:
        print(f"\nИмя '{name}'")

        #наивный алгоритм
        start_naive = time.time()
        naive_indices = naive_search(text, name)
        end_naive = time.time()

        naive_search_time = end_naive - start_naive
        naive_time_stats[name] = naive_search_time
        total_occurrences_naive += len(naive_indices)

        print(f"Наивный поиск: найдено {len(naive_indices)} упоминаний, "
              f"время {naive_search_time:.4f} секунд.")


        #КМП алгоритм
        start_kmp = time.time()
        kmp_indices = kmp_search(text, name)
        end_kmp = time.time()

        kmp_search_time = end_kmp - start_kmp
        kmp_time_stats[name] = kmp_search_time
        total_occurrences_kmp += len(kmp_indices)

        print(f"КМП поиск: найдено {len(kmp_indices)} упоминаний, "
              f"время {kmp_search_time:.4f} секунд.")

    print("Итого:")

    print(f"Общее количество упоминаний (наивный поиск): {total_occurrences_naive}")
    print(f"Общее количество упоминаний (КМП поиск): {total_occurrences_kmp}")

    print("\nВремя поиска по каждому имени (наивный алгоритм):")
    for name, t in naive_time_stats.items():
        print(f"{name}: {t:.4f} сек.")

    print("\nВремя поиска по каждому имени (КМП):")
    for name, t in kmp_time_stats.items():
        print(f"{name}: {t:.4f} сек.")


if __name__ == "__main__":
    main()
