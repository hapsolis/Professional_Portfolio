# Day 82: Morse Code Converter

Command-line Python tool that converts text to International Morse Code.

## Features
- Letters A-Z (case insensitive)
- Numbers 0-9
- Spaces become `/` for word separation
- Ignores unsupported characters
- Loop mode: enter text repeatedly or type 'quit' to exit

## Example Output
Input: `hello 123 world`  
Output: `.... . .-.. .-.. --- / .---- ..--- ...-- / .-- --- .-. .-.. -..`

## How to Run
```bash
python morse_converter.py