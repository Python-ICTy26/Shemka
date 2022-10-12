def encrypt_vigenere(plaintext: str, keyword: str) -> str:
    """
    Encrypts plaintext using a Vigenere cipher.

    >>> encrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> encrypt_vigenere("python", "a")
    'python'
    >>> encrypt_vigenere("ATTACKATDAWN", "LEMON")
    'LXFOPVEFRNHR'
    """

    ciphertext = ""
    key_l = len(keyword)
    for i, char in enumerate(plaintext):
        if char.isalpha():
            shift = ord(keyword[i % key_l]) - (65 if keyword[i % key_l].isupper() else 97)
            char_ord = ord(char)
            shifted_char_ord = char_ord + shift
            if char.isupper():
                ciphertext += chr((shifted_char_ord - 65) % 26 + 65)
            else:
                ciphertext += chr((shifted_char_ord - 97) % 26 + 97)
        else:
            ciphertext += char
    return ciphertext


def decrypt_vigenere(ciphertext: str, keyword: str) -> str:
    """
    Decrypts a ciphertext using a Vigenere cipher.

    >>> decrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> decrypt_vigenere("python", "a")
    'python'
    >>> decrypt_vigenere("LXFOPVEFRNHR", "LEMON")
    'ATTACKATDAWN'
    """
    plaintext = ""
    key_l = len(keyword)
    for i, char in enumerate(ciphertext):
        shift = ord(keyword[i % key_l]) - (65 if keyword[i % key_l].isupper() else 97)
        char_ord = ord(char)
        if char.isalpha():
            shifted_char_ord = char_ord - shift
            if char.isupper():
                plaintext += chr((shifted_char_ord - 65) % 26 + 65)
            else:
                plaintext += chr((shifted_char_ord - 97) % 26 + 97)
        else:
            plaintext += char
    return plaintext
