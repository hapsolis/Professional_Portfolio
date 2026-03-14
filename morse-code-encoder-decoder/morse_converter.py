# Morse Code Converter
# This program takes a string input from the user and converts it to International Morse Code.
# It handles letters (A-Z) and spaces. Non-supported characters are ignored.
# The program runs in a loop until the user types 'quit' to exit.

# Dictionary mapping characters to their Morse Code equivalents
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
    'Z': '--..', '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
    ' ': '/'  # Space is represented as '/' in Morse for word separation
}


def text_to_morse(text):
    """
    Converts the input text to Morse Code.
    - Converts text to uppercase for consistency.
    - Ignores any characters not in the MORSE_CODE_DICT.
    - Joins Morse codes with spaces.
    """
    text = text.upper()  # Morse is case-insensitive, so standardize to uppercase
    morse_code = []
    for char in text:
        if char in MORSE_CODE_DICT:
            morse_code.append(MORSE_CODE_DICT[char])
    return ' '.join(morse_code)

#================================== Main program loop =================================================

print("Welcome to the Morse Code Converter!")
print("Enter text to convert to Morse Code, or type 'quit' to exit.")

while True:
    user_input = input("Enter your text: ").strip()

    if user_input.lower() == 'quit':
        print("Goodbye!")
        break

    if not user_input:
        print("Please enter some text.")
        continue

    morse_output = text_to_morse(user_input)
    print(f"Morse Code: {morse_output}")
    print()  # Empty line for readability