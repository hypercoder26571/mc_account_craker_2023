import os
import platform
import json
import time
from datetime import datetime
import subprocess
import bcrypt
from colorama import init, Fore

def encrypt_password(password):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed_password

def login():
    correct_password_hash = b'$2a$12$NyhGNDsTqOVsRJHsqUcjNeWMz27QdxtZi3g0si9C70uCpzFvaxQGa'

    while True:
        entered_password = input(f"{Fore.YELLOW}Wpisz hasło do zalogowania sie do programu: {Fore.RESET}")
        hashed_entered_password = encrypt_password(entered_password)
        
        if bcrypt.checkpw(entered_password.encode(), correct_password_hash):
            print(f"{Fore.GREEN}Poprawne hasło. Logowanie udane. Przechodzenie do programu...{Fore.RESET}")
            return True
        else:
            print(f"{Fore.RED}Niepoprawne hasło. Spróbuj ponownie.{Fore.RESET}")

def read_file_lines_safe(filename):
    try:
        with open(filename, 'rb') as file:
            for line_bytes in file:
                line = None
                for enc in ('utf-8', 'cp1250', 'iso-8859-2', 'latin-1'):
                    try:
                        line = line_bytes.decode(enc)
                        break
                    except UnicodeDecodeError:
                        continue
                if line is None:
                    line = line_bytes.decode('latin-1', errors='replace')
                yield line
    except FileNotFoundError:
        return

def read_usernames_and_passwords(filename):
    if not os.path.exists(filename):
        print(f"Nie znaleziono pliku '{filename}'. Upewnij się, że plik istnieje.")
        return None
    usernames_passwords_ips = {}
    for line in read_file_lines_safe(filename):
        line = line.strip()
        if not line:
            continue
        parts = line.split(',')
        if len(parts) >= 3:
            username = parts[0]
            ip1 = parts[1]
            ip2 = parts[2]
            encoded_password = parts[-1].split(':')[-1]
            usernames_passwords_ips[username.lower()] = (username, encoded_password, ip1, ip2)
    return usernames_passwords_ips

def read_decoded_passwords(filename):
    if not os.path.exists(filename):
        print(f"Nie znaleziono pliku '{filename}'. Upewnij się, że plik istnieje.")
        return {}
    decoded_passwords = {}
    for line in read_file_lines_safe(filename):
        line = line.strip()
        if not line or ':' not in line:
            continue
        parts = line.split(':', 1)
        encoded_password = parts[0]
        decoded_password = parts[1]
        decoded_passwords[encoded_password] = decoded_password
    return decoded_passwords

def read_premium_accounts(filename):
    if not os.path.exists(filename):
        print(f"Nie znaleziono pliku '{filename}'. Upewnij się, że plik istnieje.")
        return []
    premium_accounts = []
    for line in read_file_lines_safe(filename):
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            if data.get('authorization', {}).get('premium'):
                premium_accounts.append(data.get('name'))
        except json.JSONDecodeError as e:
            print(f"Błąd dekodowania JSON: {e}")
    return premium_accounts

def save_user_data(filename, username, encoded_password, ip1, ip2, decoded_passwords, related_passwords):
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(f"\n------------------\n")
        file.write(f"Zapisano Dnia: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        file.write(f"Użytkownik: {username}\n")
        file.write(f"Hasło: {decoded_passwords.get(encoded_password, 'Nieznane')}\n")
        file.write(f"Pierwsze IP: {ip1}\n")
        file.write(f"Drugie IP: {ip2}\n")
        file.write("\nPowiązane hasła:\n")
        for related_pw in related_passwords:
            file.write(f"  - {decoded_passwords.get(related_pw, 'Nieznane')}\n")
        file.write(f"------------------\n")

def clear_console():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def print_help():
    print(f"{Fore.GREEN}Dostępne komendy:{Fore.RESET}")
    print(f"- {Fore.RED}konta{Fore.RESET}: Otwiera plik tekstowy '{Fore.YELLOW}konta.txt{Fore.RESET}', gdzie przechowywane są dane użytkowników.")
    print(f"- {Fore.RED}help{Fore.RESET}: Wyświetla dostępne komendy.")
    print(f"- {Fore.RED}l{Fore.RESET}: Zamyka program.")

def main():
    # Logowanie
    if not login():
        return

    # Inicjalizacja colorama
    init()

    data_filename = 'data.txt'
    cracked_filename = 'cracked.txt'
    save_filename = 'konta.txt'
    accounts_filename = 'accounts.json'

    usernames_passwords_ips = read_usernames_and_passwords(data_filename)
    if not usernames_passwords_ips:
        return  # Zwróć z funkcji, jeśli nie udało się odczytać danych użytkowników

    decoded_passwords = read_decoded_passwords(cracked_filename)
    premium_accounts = read_premium_accounts(accounts_filename)

    displayed_passwords = set()

    while True:  
        clear_console()  
        print(f"Witaj, {Fore.YELLOW}HyperCoder26571!{Fore.RESET}, Wpisz '{Fore.GREEN}help{Fore.RESET}' żeby wyświetlić listę komend")
        username = input(f"Wpisz nazwę użytkownika, którego hasło chcesz wyświetlić (lub '{Fore.RED}l{Fore.RESET}' aby zakończyć): ").lower()

        if username == 'l':
            break

        if username == 'konta':
            try:
                subprocess.Popen(['notepad', save_filename])
                print("Plik 'konta.txt' został otwarty.")
            except FileNotFoundError:
                print(f"Nie udało się otworzyć pliku '{save_filename}'. Sprawdź ścieżkę pliku.")
            continue

        if username == 'help':
            print_help()
            input(f"Naciśnij {Fore.YELLOW}Enter{Fore.RESET}, aby kontynuować...")
            continue

        if username in usernames_passwords_ips:
            original_username, encoded_password, ip1, ip2 = usernames_passwords_ips[username]
            password = decoded_passwords.get(encoded_password, 'Nieznane')
            
            if password not in displayed_passwords:
                print(f"\nDane hasło użytkownika '{Fore.GREEN}{original_username}{Fore.RESET}': {Fore.RED}{password}{Fore.RESET}")
                displayed_passwords.add(password)
                
            print(f"{Fore.YELLOW}Pierwsze IP użytkownika '{Fore.GREEN}{original_username}{Fore.RESET}': {Fore.YELLOW}{ip1}{Fore.RESET}")
            print(f"{Fore.YELLOW}Drugie IP użytkownika '{Fore.GREEN}{original_username}{Fore.RESET}': {Fore.YELLOW}{ip2}{Fore.RESET}")

            print(f"\nPowiązane hasła z pierwszym IP:")
            related_passwords = []
            for user, (orig_user, enc_pw, ip1_, ip2_) in usernames_passwords_ips.items():
                if ip1_ == ip1:
                    related_password = decoded_passwords.get(enc_pw, 'Nieznane')
                    if related_password not in displayed_passwords:
                        related_passwords.append(enc_pw)
                        displayed_passwords.add(related_password)
                        print(f"  - {Fore.RED}{related_password}{Fore.RESET}")

            print(f"\nPowiązane hasła z drugim IP:")
            for user, (orig_user, enc_pw, ip1_, ip2_) in usernames_passwords_ips.items():
                if ip2_ == ip2:
                    related_password = decoded_passwords.get(enc_pw, 'Nieznane')
                    if related_password not in displayed_passwords:
                        related_passwords.append(enc_pw)
                        displayed_passwords.add(related_password)
                        print(f"  - {Fore.RED}{related_password}{Fore.RESET}")

            save_choice = input("Czy chcesz zapisać te dane do pliku? (t/n): ").lower()
            if save_choice == 't':
                save_user_data(save_filename, original_username, encoded_password, ip1, ip2, decoded_passwords, related_passwords)
                print("Dane zostały pomyślnie zapisane do pliku.")
            elif save_choice == 'n':
                print("Dane nie zostały zapisane.")
        elif username in premium_accounts:
            print("Użytkownik posiada konto premium.")
            print("Ponowne wpisywanie nazwy użytkownika za 5 sekund...")
            time.sleep(5)
        else:
            print(f"Użytkownik o nazwie '{Fore.GREEN}{username.capitalize()}{Fore.RESET}' nie został znaleziony.")

if __name__ == "__main__":
    main()
