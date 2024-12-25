import math
from bitarray import bitarray
import os

class LZ77Compressor:
    """
    Класс LZ77Compressor реализует базовый механизм сжатия (компрессии) и распаковки (декомпрессии)
    по алгоритму LZ77. Он умеет:

    1) compress(...)   - сжимать файл, используя "окно" поиска повторов и выводить результат
                         в битовый поток (или в бинарный файл).
    2) decompress(...) - распаковывать ранее сжатый файл, восстанавливая исходные данные.
    """

    # Максимальный размер "окна" (window) для поиска повторов.
    # Слишком большое окно может быть неэффективно для тестового кода.
    MAX_WINDOW_SIZE = 400  

    def __init__(self, window_size=20):
        """
        :param window_size: Размер "окна" поиска совпадений (distance). 
                            Будет взят минимум из window_size и MAX_WINDOW_SIZE.
                            Чем больше окно, тем лучше потенциальное сжатие, 
                            но тем медленнее работает алгоритм.
        """
        self.window_size = min(window_size, self.MAX_WINDOW_SIZE)
        self.lookahead_buffer_size = 15

    def compress(self, input_file_path, output_file_path=None, verbose=False):
        """
        Считывает данные из input_file_path, сжимает их по LZ77 и либо:
          - записывает результат в output_file_path (бинарный файл), если он указан
          - возвращает результат как bitarray, если output_file_path = None

        :param input_file_path:  Путь к входному файлу (исходный).
        :param output_file_path: Путь к выходному файлу (сжатому). 
                                 Если None, результат возвращается в виде bitarray.
        :param verbose:          Если True, печатает процесс сжатия (флаги, смещения и т.д.).
        :return:                 None или bitarray (см. выше)
        """
        data = None
        i = 0  # текущая позиция в исходных данных
        output_buffer = bitarray(endian='big')  # выходной буфер (битовый)

        # 1) Считываем все байты из входного файла
        try:
            with open(input_file_path, 'rb') as input_file:
                data = input_file.read()
        except FileNotFoundError:
            print(f'Ошибка: файл "{input_file_path}" не найден. Проверьте путь и попробуйте снова.')
            return
        except IOError as e:
            print(f'Ошибка при чтении файла "{input_file_path}": {e}')
            return

        # 2) Идём по массиву data, пока не дойдем до конца
        while i < len(data):
            # Находим самое длинное совпадение (distance, length) 
            # для подстроки, начинающейся в позиции i
            match = self.findLongestMatch(data, i)

            if match:
                # Если нашли совпадение, записываем его в формат:
                #   1 (бит флага), 
                #   затем 12 бит (distance = расстояние назад),
                #   затем 4 бита (length = длина совпадения).
                (bestMatchDistance, bestMatchLength) = match

                # Добавляем бит "1" (говорит, что дальше идут distance/length)
                output_buffer.append(True)

                # Записываем distance (12 бит), разбитые на 2 байта:
                #  - старшие 8 бит: bestMatchDistance >> 4
                #  - младшие 4 бита: (bestMatchDistance & 0xF)
                #    в сочетании со 4 битами length => один байт

                # Старший байт distance:
                distance_high = bestMatchDistance >> 4
                output_buffer.frombytes(bytes([distance_high]))
                # Младшие 4 бита distance + 4 бита length:
                distance_low_length = ((bestMatchDistance & 0xf) << 4) | bestMatchLength
                output_buffer.frombytes(bytes([distance_low_length]))

                if verbose:
                    print(f"<1, dist={bestMatchDistance}, len={bestMatchLength}> ", end='')

                # Сдвигаем i вперёд на длину совпадения
                i += bestMatchLength

            else:
                # Если совпадение не найдено, пишем 
                #   0 (бит флага), 
                #   затем 8 бит (1 байт символа)
                output_buffer.append(False)
                output_buffer.frombytes(bytes([data[i]]))

                if verbose:
                    print(f"<0, char={data[i]}> ", end='')

                i += 1

        # В конце нужно, чтобы общее число бит было кратно 8.
        # fill() дополняет нулями до ближайшего байта
        output_buffer.fill()

        # 3) Если указан файл для записи - пишем в него байты
        if output_file_path:
            try:
                with open(output_file_path, 'wb') as output_file:
                    output_file.write(output_buffer.tobytes())
                if verbose:
                    print("\nФайл сжат и сохранен.")
                return None
            except IOError as e:
                print(f'Ошибка при записи в файл "{output_file_path}": {e}')
                return

        # Если не указан выходной файл - возвращаем bitarray
        return output_buffer

    def decompress(self, input_file_path, output_file_path=None):
        """
        Распаковывает (декодирует) данные из бинарного файла (input_file_path),
        восстанавливая исходную последовательность байт.

        :param input_file_path:  Путь к сжатому LZ77 файлу.
        :param output_file_path: Путь к результату распаковки (исходный файл).
                                 Если None, метод вернёт bytes (массив байтов).
        :return:                 None или bytes (см. выше).
        """
        data_bits = bitarray(endian='big')
        output_buffer = []

        # 1) Считываем битовый поток из файла
        try:
            with open(input_file_path, 'rb') as input_file:
                data_bits.fromfile(input_file)
        except FileNotFoundError:
            print(f'Ошибка: файл "{input_file_path}" не найден. Проверьте путь и попробуйте снова.')
            return
        except IOError as e:
            print(f'Ошибка при чтении файла "{input_file_path}": {e}')
            return

        # 2) Парсим бит за битом
        while len(data_bits) >= 9:  # нужно хотя бы 1 бит флага + 8 бит на символ
            # Считываем флаг
            flag = data_bits.pop(0)  # pop(0) извлекает первый бит

            if not flag:
                # Если флаг = 0 -> следующий байт - это несжатый символ
                if len(data_bits) < 8:
                    print("Предупреждение: недостаточно бит для декодирования символа.")
                    break
                byte_as_bits = data_bits[:8]  # первые 8 бит
                byte_val = byte_as_bits.tobytes()  # это будет bytes длиной 1
                output_buffer.append(byte_val)
                del data_bits[:8]  # удаляем прочитанные 8 бит

            else:
                # Если флаг = 1 -> дальше идут 12 бит distance и 4 бита length
                # Для удобства в коде берут: 
                #   byte1 = старшие 8 бит distance 
                #   byte2 = 4 бита младших distance + 4 бита length

                if len(data_bits) < 16:
                    print("Предупреждение: недостаточно бит для декодирования (distance, length).")
                    break

                # Извлекаем следующие 16 бит
                byte1_bits = data_bits[:8]
                byte2_bits = data_bits[8:16]

                byte1 = byte1_bits.tobytes()[0]  # получаем int значение
                byte2 = byte2_bits.tobytes()[0]

                del data_bits[:16]

                # distance = (byte1 << 4) | (byte2 >> 4)
                # length = byte2 & 0xF
                distance = (byte1 << 4) | (byte2 >> 4)
                length = (byte2 & 0xf)

                if distance == 0:
                    print("Предупреждение: distance равен 0. Пропуск.")
                    continue

                # Теперь восстанавливаем length байт, которые находятся на distance позиций назад
                # Это аналог "копирования" предыдущей последовательности в выход
                for _ in range(length):
                    if distance > len(output_buffer):
                        print("Ошибка: distance больше текущего размера выходного буфера.")
                        break
                    byte_to_copy = output_buffer[-distance]
                    output_buffer.append(byte_to_copy)

        # Склеиваем все байты
        out_data = b''.join(output_buffer)

        # 3) Если указан выходной файл - записываем результат
        if output_file_path:
            try:
                with open(output_file_path, 'wb') as output_file:
                    output_file.write(out_data)
                print('Файл успешно распакован и сохранен.')
                return None
            except IOError as e:
                print(f'Ошибка при записи в файл "{output_file_path}": {e}')
                return

        # Иначе просто возвращаем bytes
        return out_data

    def findLongestMatch(self, data, current_position):
        """
        Находит самое длинное совпадение (match) для подстроки, начинающейся в current_position,
        в пределах "окна" размера self.window_size, расположенного позади current_position.

        Возвращает кортеж (bestMatchDistance, bestMatchLength) или None, если совпадение не найдено.
        """
        end_of_buffer = min(current_position + self.lookahead_buffer_size, len(data) + 1)

        best_match_distance = -1
        best_match_length = -1

        # Ищем подстроки длиной >= 2 (так как 1 байт не выгодно кодировать distance/length).
        for j in range(current_position + 2, end_of_buffer):
            # Возьмём подстроку, которую хотим найти.
            substring = data[current_position:j]

            # Начало окна: не раньше, чем current_position - window_size
            start_index = max(0, current_position - self.window_size)

            # Идём по всему окну
            for i in range(start_index, current_position):
                # Проверим, совпадает ли substring с данными, начиная с i
                # Оптимизированное сравнение без повторений
                if data[i:i + len(substring)] == substring:
                    if len(substring) > best_match_length:
                        best_match_distance = current_position - i
                        best_match_length = len(substring)

        if best_match_distance > 0 and best_match_length > 0:
            return (best_match_distance, best_match_length)
        return None


# -------------------------- Пример использования -------------------------- #
if __name__ == "__main__":
    """
    Этот блок будет выполнен, если запустить файл напрямую: `python lz77_compressor.py`
    """

    compressor = LZ77Compressor(window_size=20)

    # Определите пути к файлам
    input_file = 'war_and_peace.txt'       # Убедитесь, что этот файл существует
    compressed_file = 'war_and_peace.lz77' # Имя сжатого файла
    decompressed_file = 'war_and_peace_out.txt' # Имя распакованного файла

    # Сжимаем:
    print(f"Сжатие файла '{input_file}' в '{compressed_file}'...")
    compressor.compress(
        input_file_path=input_file,
        output_file_path=compressed_file,
        verbose=True
    )

    # Проверка, был ли файл успешно сжат
    if os.path.exists(compressed_file):
        # Распаковываем:
        print(f"\nРаспаковка файла '{compressed_file}' в '{decompressed_file}'...")
        compressor.decompress(
            input_file_path=compressed_file,
            output_file_path=decompressed_file
        )

        # Расчет Степени Сжатия (SSR)
        def calculate_ssr(src_path, comp_path):
            Ssrc = os.path.getsize(src_path)
            Scomp = os.path.getsize(comp_path)
            SSR = (1 - Scomp / Ssrc) * 100
            return SSR

        if os.path.exists(decompressed_file):
            ssr = calculate_ssr(input_file, compressed_file)
            print(f"\nСтепень сжатия (SSR): {ssr:.2f}%")

            # Сравнение исходного и распакованного файлов
            print("\nСравнение исходного и распакованного файлов:")
            try:
                with open(input_file, 'rb') as f1, open(decompressed_file, 'rb') as f2:
                    src_data = f1.read()
                    dec_data = f2.read()
                    if src_data == dec_data:
                        print("Файлы идентичны.")
                    else:
                        print("Файлы отличаются.")
            except IOError as e:
                print(f"Ошибка при чтении файлов для сравнения: {e}")
        else:
            print("Ошибка: Распакованный файл не был создан.")
    else:
        print("Ошибка: Сжатый файл не был создан.")
