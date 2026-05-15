print("===== CAESAR CIPHER =====")

message = input("Enter your message: ")
shift = int(input("Enter shift number: "))

encrypted = ""

for letter in message:
    if letter.isalpha():
        ascii_value = ord(letter)
        new_ascii = ascii_value + shift
        encrypted_letter = chr(new_ascii)
        encrypted += encrypted_letter
    else:
        encrypted += letter

print("\nEncrypted Message:", encrypted)
print("\n===== END =====")