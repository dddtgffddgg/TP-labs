import math
from bitarray import bitarray
import os

class LZ77Compressor:
    """
    Класс LZ77Compressor реализует механизм сжатия и распаковки по алгоритму LZ77.
    """

    MAX_WINDOW_SIZE = 400  

    def __init__(self, window_size=20):
        """
        :param window_size: Размер окна поиска совпадений (distance).
        """
        self.window_size = min(window_size, self.MAX_WINDOW_SIZE)
        self.lookahead_buffer_size = 15

    def compress(self, input_file_path, output_file_path=None, verbose=False):
        data = None
        i = 0  # текущая позиция в исходных данных
        output_buffer = bitarray(endian='big')  # выходной буфер (битовый)
        substring_dict = {}  # Словарь для хранения подстрок

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
            # Добавляем текущую подстроку в словарь
            if i + 2 <= len(data):
                substring = data[i:i + 2]
                if substring in substring_dict:
                    substring_dict[substring].append(i)
                else:
                    substring_dict[substring] = [i]

            # Находим самое длинное совпадение (distance, length) 
            match = self.findLongestMatch(data, i, substring_dict)

            if match:
                (bestMatchDistance, bestMatchLength) = match

                # Добавляем бит "1" (говорит, что дальше идут distance/length)
                output_buffer.append(True)

                # Записываем distance (12 бит), разбитые на 2 байта:
                distance_high = bestMatchDistance >> 4
                output_buffer.frombytes(bytes([distance_high]))
                distance_low_length = ((bestMatchDistance & 0xF) << 4) | bestMatchLength
                output_buffer.frombytes(bytes([distance_low_length]))

                if verbose:
                    print(f"<1, dist={bestMatchDistance}, len={bestMatchLength}> ", end='')

                # Сдвигаем i вперёд на длину совпадения и обновляем словарь
                for j in range(bestMatchLength):
                    if i + j + 2 <= len(data):
                        substring_new = data[i + j:i + j + 2]
                        if substring_new in substring_dict:
                            substring_dict[substring_new].append(i + j)
                        else:
                            substring_dict[substring_new] = [i + j]
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
        data_bits = bitarray(endian='big')
        output_buffer = bytearray()

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
        while len(data_bits) >= 1:
            # Считываем флаг
            flag = data_bits.pop(0)  # pop(0) извлекает первый бит

            if not flag:
                # Если флаг = 0 -> следующий байт - это несжатый символ
                if len(data_bits) < 8:
                    print("Предупреждение: недостаточно бит для декодирования символа.")
                    break
                byte_as_bits = data_bits[:8]  # первые 8 бит
                byte_val = byte_as_bits.tobytes()[0]  # получаем int значение
                output_buffer.append(byte_val)
                del data_bits[:8]  # удаляем прочитанные 8 бит

            else:
                # Если флаг = 1 -> дальше идут 12 бит distance и 4 бита length
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
                length = (byte2 & 0xF)

                if distance == 0:
                    print("Предупреждение: distance равен 0. Пропуск.")
                    continue

                # Восстанавливаем length байт, которые находятся на distance позиций назад
                start = len(output_buffer) - distance
                if start < 0:
                    print("Ошибка: distance больше текущего размера выходного буфера.")
                    break
                for _ in range(length):
                    byte_to_copy = output_buffer[start]
                    output_buffer.append(byte_to_copy)
                    start += 1  # смещаемся вперед для последовательных копирований

        # 3) Если указан выходной файл - записываем результат
        if output_file_path:
            try:
                with open(output_file_path, 'wb') as output_file:
                    output_file.write(output_buffer)
                print('Файл успешно распакован и сохранен.')
                return None
            except IOError as e:
                print(f'Ошибка при записи в файл "{output_file_path}": {e}')
                return

        # Иначе просто возвращаем bytes
        return bytes(output_buffer)

    def findLongestMatch(self, data, current_position, dictionary):
        end_of_buffer = min(current_position + self.lookahead_buffer_size, len(data) + 1)
        best_match_distance = 0
        best_match_length = 0

        # Текущая подстрока длины 2
        if current_position + 2 > len(data):
            return None
        substring = data[current_position:current_position + 2]
        if substring in dictionary:
            for match_position in dictionary[substring]:
                distance = current_position - match_position
                if distance > self.window_size:
                    continue
                match_length = 2
                while (match_length < self.lookahead_buffer_size and
                       current_position + match_length < len(data) and
                       data[match_position + match_length] == data[current_position + match_length]):
                    match_length += 1
                if match_length > best_match_length:
                    best_match_distance = distance
                    best_match_length = match_length

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
