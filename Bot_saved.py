from datetime import datetime, timedelta
from collections import UserDict
import pickle


class Field:
    def __init__(self, value=None):
        self._value = value

    def __str__(self):
        return str(self._value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value


class Name(Field):
    pass


class Phone(Field):
    @Field.value.setter
    def value(self, new_value):
        if len(new_value) != 10 or not new_value.isdigit():
            raise ValueError("Invalid phone number")
        self._value = new_value


class Birthday(Field):
    @Field.value.setter
    def value(self, new_value):
        try:
            datetime.strptime(new_value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid birthday format. Please use dd.mm.yyyy")
        self._value = new_value


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if str(phone) == old_phone:
                phone.value = new_phone
                break

    def days_to_birthday(self):
        if self.birthday:
            now = datetime.now().date()
            birthday = datetime.strptime(self.birthday.value, "%d.%m.%Y").date().replace(year=now.year)
            if now > birthday:
                birthday = birthday.replace(year=now.year + 1)
            return (birthday - now).days
        return None

    def __str__(self):
        result = f"Name: {self.name}\n"
        if self.phones:
            result += "Phones:\n"
            for phone in self.phones:
                result += f"- {phone}\n"
        if self.birthday:
            result += f"Birthday: {self.birthday}\n"
            days_to_birthday = self.days_to_birthday()
            if days_to_birthday is not None:
                result += f"Days to birthday: {days_to_birthday}\n"
        return result


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[str(record.name)] = record

    def search_records(self, search_term):
        result = []
        for record in self.data.values():
            name = str(record.name).lower()
            phones = [str(phone).lower() for phone in record.phones]
            if search_term.lower() in name or any(search_term.lower() in phone for phone in phones):
                result.append(record)
        return result

    def save_to_file(self, filename):
        with open(filename, "wb") as file:
            pickle.dump(self.data, file)

    def load_from_file(self, filename):
        with open(filename, "rb") as file:
            self.data = pickle.load(file)

    def iterator(self, page_size=10):
        records = list(self.data.values())
        total_pages = (len(records) - 1) // page_size + 1
        current_page = 1
        while current_page <= total_pages:
            start_index = (current_page - 1) * page_size
            end_index = start_index + page_size
            yield records[start_index:end_index]
            current_page += 1


def main():
    address_book = AddressBook()

    while True:
        user_input = input("> ").lower().split(" ", 1)
        command = user_input[0]

        if command == "hello":
            print("How can I help you?")

        elif command == "add":
            try:
                name, *args = user_input[1].split(" ")
                if name and args:
                    record = Record(name)
                    for arg in args:
                        if arg.startswith("phone="):
                            phone = arg.split("=")[1]
                            record.add_phone(phone)
                        elif arg.startswith("birthday="):
                            birthday = arg.split("=")[1]
                            record.birthday = Birthday(birthday)
                        else:
                            print(f"Invalid argument: {arg}")
                            break
                    else:
                        address_book.add_record(record)
                        print("Contact added successfully!")
                else:
                    print("Invalid input format!")
            except IndexError:
                print("Give me name and phone please")

        elif command == "change":
            try:
                name, *args = user_input[1].split(" ")
                if name and args:
                    records = address_book.search_records(name=name)
                    if records:
                        for record in records:
                            for arg in args:
                                if arg.startswith("phone="):
                                    old_phone, new_phone = arg.split("=")[1].split(",")
                                    record.edit_phone(old_phone, new_phone)
                                else:
                                    print(f"Invalid argument: {arg}")
                                    break
                        else:
                            print("Contact updated successfully!")
                    else:
                        print("Contact not found!")
                else:
                    print("Invalid input format!")
            except IndexError:
                print("Give me name and phone please")

        elif command == "phone":
            try:
                name = user_input[1]
                if name:
                    records = address_book.search_records(name=name)
                    if records:
                        for record in records:
                            phones = [str(phone) for phone in record.phones]
                            print("\n".join(phones))
                    else:
                        print("Contact not found!")
                else:
                    print("Enter user name")
            except IndexError:
                print("Enter user name")

        elif command == "search":
            if len(user_input) > 1:
                search_term = user_input[1]
                results = address_book.search_records(search_term)
                if results:
                    for record in results:
                        print(record)
                else:
                    print("No matching records found.")
            else:
                print("Invalid input format!")

        elif command == "show":
            if len(user_input) == 1 or user_input[1] == "all":
                if address_book.data:
                    for record in address_book.data.values():
                        print(record)
                else:
                    print("No contacts found!")
            else:
                print("Invalid command")

        elif command == "pages":
            try:
                page_size = int(user_input[1])
                if page_size <= 0:
                    print("Page size must be a positive integer")
                else:
                    iterator = address_book.iterator(page_size=page_size)
                    for page in iterator:
                        for record in page:
                            print(record)
                        user_input = input("Press enter to continue or 'exit' to quit: ")
                        if user_input.lower() == "exit":
                            break
                        print()
                    else:
                        print("No more records to display")
            except ValueError:
                print("Invalid page size")

        elif command == "save":
            try:
                filename = user_input[1]
                address_book.save_to_file(filename)
                print(f"Address book saved to {filename}")
            except IndexError:
                print("Enter filename")

        elif command == "load":
            try:
                filename = user_input[1]
                address_book.load_from_file(filename)
                print(f"Address book loaded from {filename}")
            except FileNotFoundError:
                print("File not found")
            except IndexError:
                print("Enter filename")

        elif command == "exit":
            break

        else:
            print("Invalid command. Type 'hello' for assistance.")


if __name__ == "__main__":
    main()
