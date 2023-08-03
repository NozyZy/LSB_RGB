import argparse
import os.path

from PIL import Image


def convert_bytes_to_bits(text):
    return ''.join(format(i, '08b') for i in text)


def convert_str_to_bits(text):
    return ''.join(format(ord(i), '08b') for i in text)


def convert_bits_to_str(bits):
    return ''.join(chr(int(''.join(x), 2)) for x in zip(*[iter(bits)] * 8))


def change_int_value_bit(bits, value, position=0):
    if value not in '01':
        raise ValueError('Value needs to be 0 or 1.')
    if not 0 <= position <= 7:
        raise ValueError('Position needs to be between 0 and 7 included.')

    s = list(get_bits_from_int(bits))
    position = 7 - position
    s[position] = value
    return int(''.join(s), 2)


def get_bits_from_int(value):
    return f'{value:08b}'


def bitstring_to_bytes(s):
    return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big')


parser = argparse.ArgumentParser(
    prog='LSB embedder and extractor',
    description='Extracts and embed text into PNG images. Horizontally, vertically and diagonally')

parser.add_argument('image',
                    type=str,
                    help='Image to embed/extract data')
parser.add_argument('-t', '--text',
                    type=str,
                    default=None,
                    required=False,
                    help='Text to be embed')
parser.add_argument('-f', '--file',
                    type=str,
                    default=None,
                    required=False,
                    help='File to be embed (.txt in plain text, other in binary)')
parser.add_argument('-d', '--direction',
                    type=str,
                    default='horizontal',
                    choices=['horizontal', 'vertical', 'diagonal'],
                    nargs='?',
                    help='Direction to embed')
parser.add_argument('-o', '--output',
                    type=str,
                    default=None,
                    required=False,
                    help="File to output extracted data (.txt in plain text, other in binary)")

args = parser.parse_args()

if not os.path.isfile(args.image):
    parser.error(f'Image {args.image} does not exists.')

if args.file and not os.path.isfile(args.file):
    parser.error(f'File {args.image} does not exists.')

# Open image to embed in or to be extracted from
img = Image.open(args.image).convert('RGB')

if args.direction == 'diagonal' and img.height != img.width:
    print('Diagonal extraction and embedding only works on square images.')
direction = args.direction

# Embedding mode
if args.text or args.file:

    # Get data from file or text
    data = ''
    if args.file:
        mode = 'r' if args.file.endswith('.txt') else 'rb'
        f = open(args.file, mode)
        data = f.read()
        f.close()
        print('[+] Embedding file :', args.file)
    elif args.text:
        data = args.text
        print('[+] Embedding data :', data)

    # Size check
    size = img.width
    if direction == 'diagonal' and len(data) * 8 > size:
        parser.error(f'Your text not should exceed {size // 8} for that image in diagonal.')
    elif len(data) * 8 > img.width * img.height:
        parser.error('Not enough space to embed data.')
    print(f'[+] Embedding {len(data) // 8} bytes')

    # Begin Embedding

    # convert data to binary format
    if type(data) == 'str':
        to_embed = convert_str_to_bits(data)
    else:
        try:
            to_embed = convert_bytes_to_bits(data)
        except:
            raise TypeError(f'Cannot convert data type {type(data)}')

    # diagonal direction
    if direction == 'diagonal':
        for i in range(len(to_embed)):
            pixel = list(img.getpixel((i, i)))
            pixel[i % 3] = change_int_value_bit(pixel[i % 3], to_embed[i])
            img.putpixel((i, i), tuple(pixel))

    # horizontal or vertical directions
    else:
        total = 0
        for i in range(img.height):
            if total >= len(to_embed):
                break
            for j in range(img.width):
                if total >= len(to_embed):
                    break
                couple = (j, i) if direction == 'horizontal' else (i, j)
                pixel = list(img.getpixel(couple))
                pixel[total % 3] = change_int_value_bit(pixel[total % 3], to_embed[total])
                img.putpixel((j, i), tuple(pixel))
                total += 1

    img.save('embedded.png', 'PNG')
    print('[+] Data embedded successfully to embedded.png')


# Extraction mode
else:
    print('[+] Extracting data')

    # diagonal direction
    if direction == 'diagonal':
        data = ''
        for i in range(img.height):
            pixel = img.getpixel((i, i))
            data += get_bits_from_int(pixel[i % 3])[-1]

    # horizontal or vertical directions
    else:
        data = ''
        total = 0
        sanitize_count = 12 if args.output else 2
        for i in range(img.height):
            if (total > 8 * (sanitize_count + 1) and
                    (data[len(data) - 8 * sanitize_count:] == '0' * 8 * sanitize_count or
                     data[len(data) - 8 * sanitize_count:] == '1' * 8 * sanitize_count)):
                data = data[:len(data) - 8 * sanitize_count]
                break
            for j in range(img.width):
                couple = (j, i) if direction == 'horizontal' else (i, j)
                pixel = img.getpixel(couple)
                data += get_bits_from_int(pixel[total % 3])[-1]
                total += 1
                if (total > 8 * (sanitize_count + 1) and
                        (data[len(data) - 8 * sanitize_count:] == '0' * 8 * sanitize_count or
                         data[len(data) - 8 * sanitize_count:] == '1' * 8 * sanitize_count)):
                    data = data[:len(data) - 8 * sanitize_count]
                    break
    if not data:
        print('[-] No data was found.')
    elif args.output:
        with open(args.output, 'wb') as f:
            f.write(bitstring_to_bytes(data))
        print(f'[+] Successfully extracted {len(data)} bytes to {args.output}')
    else:
        print(f'[+] Extracted data : {convert_bits_to_str(data)}')
