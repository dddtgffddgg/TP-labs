import os
from bitarray import bitarray
from bitarray.util import ba2int, int2ba

class LZ77Compressor:
    MAX_WINDOW_SIZE = 500  #максимальный размер окна поиска
    MAX_LOOKAHEAD_BUFFER_SIZE = 15  #максимальный размер буфера просмотра
    MAX_MATCH_LENGTH = 15  #максимальная длина совпадения (4 бита)

    def __init__(self, window_size=20):
        self.window_size = min(window_size, self.MAX_WINDOW_SIZE)
        self.lookahead_buffer_size = self.MAX_LOOKAHEAD_BUFFER_SIZE

    def compress(self, input_file_path, output_file_path=None, verbose=False):
        #cжимает данные из входного файла по алгоритму LZ77

        try:
            with open(input_file_path, 'rb') as f:
                data = f.read()
        except FileNotFoundError:
            print(f'Ошибка: файл "{input_file_path}" не найден.')
            return False 
        except IOError as e:
            print(f'Ошибка при чтении файла "{input_file_path}": {e}')
            return False

        i = 0
        output_bits = bitarray(endian='big') #хранение сжатых данных

        while i < len(data):
            match_distance, match_length = self.find_longest_match(data, i)

            if match_length > 1:
                #ограничеснная длина совпадения
                match_length = min(match_length, self.MAX_MATCH_LENGTH)

                #флаг = 1 при совпадении
                output_bits.append(1)

                #distance 12 бит
                distance_bits = int2ba(match_distance, length=12)
                output_bits.extend(distance_bits)

                #length 4 бита
                length_bits = int2ba(match_length, length=4)
                output_bits.extend(length_bits)

                if verbose:
                    print(f"(1, {match_distance}, {match_length}) ", end='')

                i += match_length
            else:
                #флаг = 0 если нет совпадений
                output_bits.append(0)

                #символ 8 бит
                symbol_bits = int2ba(data[i], length=8)
                output_bits.extend(symbol_bits)

                if verbose:
                    print(f"(0, {data[i]}) ", end='')

                i += 1

        #дополние поток до полного байта 16 бит
        output_bits.fill()

        #если сжатый файл меньше исхожного - сохраняем
        if output_file_path:
            compressed_size = len(output_bits) // 8
            original_size = len(data)
            if compressed_size < original_size:
                try:
                    with open(output_file_path, 'wb') as f:
                        f.write(output_bits.tobytes())
                    if verbose:
                        print("\nФайл сжат и сохранен.")
                    return True 
                except IOError as e:
                    print(f'Ошибка при записи в файл "{output_file_path}": {e}')
                    return False
            else:
                print("Сжатый файл больше или равен исходному. Сохранение исходного файла не выполнено.")
                return False 
        else:
            return output_bits
        
    #распаковка данных из сжатого файла
    def decompress(self, input_file_path, output_file_path=None):

        try:
            with open(input_file_path, 'rb') as f:
                compressed_bits = bitarray(endian='big')
                compressed_bits.fromfile(f)
        except FileNotFoundError:
            print(f'Ошибка: файл "{input_file_path}" не найден.')
            return
        except IOError as e:
            print(f'Ошибка при чтении файла "{input_file_path}": {e}')
            return

        i = 0
        output_data = bytearray() 

        while i < len(compressed_bits):
            flag = compressed_bits[i]
            i += 1

            if flag:
                #если флаг = 1, то читает 12 бит distance и 4 бита length
                if i + 16 > len(compressed_bits):
                    #достаточно бит для триплета
                    break  

                distance_bits = compressed_bits[i:i+12]
                distance = ba2int(distance_bits) 
                i += 12

                length_bits = compressed_bits[i:i+4]
                length = ba2int(length_bits)
                i += 4

                if distance > len(output_data):
                    print("Ошибка: distance больше текущего размера выходного буфера.")
                    break

                for _ in range(length):
                    byte = output_data[-distance]
                    output_data.append(byte)
            else:
                #если флаг =0, то читает 8 бит символа 
                if i + 8 > len(compressed_bits):
                    #достаточно бит для символа
                    break  #прекращает декомпрессию без предупреждений

                symbol_bits = compressed_bits[i:i+8]
                symbol = ba2int(symbol_bits)
                output_data.append(symbol)
                i += 8

        if output_file_path:
            try:
                with open(output_file_path, 'wb') as f:
                    f.write(output_data)
                print('Файл успешно распакован и сохранен.')
            except IOError as e:
                print(f'Ошибка при записи в файл "{output_file_path}": {e}')
        else:
            return bytes(output_data)


    def find_longest_match(self, data, current_position):

        #ищет самое длинное совпадение в окне, возвращает кортеж если есть совпадение, если совпадений нет, возвращает (0, 0).
        end_of_buffer = min(current_position + self.lookahead_buffer_size, len(data)) #конец буффера просмотра

        best_match_distance = 0
        best_match_length = 0

        window_start = max(0, current_position - self.window_size)  #начало окна поиска

        for j in range(current_position + 1, end_of_buffer + 1):
            substring = data[current_position:j]
            start_index = data.find(substring, window_start, current_position)

            #если совпадение найдено
            if start_index != -1:
                match_length = j - current_position  #вычисление длины
                match_distance = current_position - start_index #вычисление расстояния

                if match_length > best_match_length:
                    best_match_length = match_length
                    best_match_distance = match_distance
            else: 
                break #если совпадение не найдено прекращает поиск

        return (best_match_distance, best_match_length) if best_match_distance > 0 else (0, 0)

if __name__ == "__main__":
    compressor = LZ77Compressor(window_size=300)  # Увеличиваем window_size для лучшего сжатия

    input_file = 'war_and_peace.txt'      
    compressed_file = 'war_and_peace.lz77' # имя сжатого файла
    decompressed_file = 'war_and_peace_out.txt' # имя распакованного файла

    # Сжатие
    print(f"Сжатие файла '{input_file}' в '{compressed_file}'...")
    was_compressed = compressor.compress(
        input_file_path=input_file,
        output_file_path=compressed_file,
        verbose=True
    )

    if was_compressed:
        print(f"\nРаспаковка файла '{compressed_file}' в '{decompressed_file}'...")
        compressor.decompress(
            input_file_path=compressed_file,
            output_file_path=decompressed_file
        )

        #степень сжатия
        def calculate_ssr(src_path, comp_path):
            Ssrc = os.path.getsize(src_path)
            Scomp = os.path.getsize(comp_path)
            SSR = (1 - Scomp / Ssrc) * 100
            return SSR

        if os.path.exists(decompressed_file):
            ssr = calculate_ssr(input_file, compressed_file)
            print(f"\nСтепень сжатия (SSR): {ssr:.2f}%")

            #сравнение исходного и распакованного файлов
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
        print("Сжатие не было выполнено, так как сжатый файл не уменьшился в размере.")
