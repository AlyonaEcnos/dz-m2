from models import Record, AddressBook
import json
import os

class InputError(Exception):
    pass

class DataHandler:
    def __init__(self, file_path):
        self.file_path = file_path

    def save_data(self, records):
        with open(self.file_path, "w") as file:
            data = {
                "records": [record.__json__() for record in records]
            }
            json.dump(data, file)

    def load_data(self):
        try:
            if os.path.getsize(self.file_path) > 0:  
                with open(self.file_path, "r") as file:
                    data = json.load(file)
                    records = [Record(record["name"], record.get("birthday")) for record in data.get("records", [])]
                    for i, record in enumerate(records):
                        if "phones" in data.get("records", [])[i]:
                            for phone in data["records"][i]["phones"]:
                                record.add_phone(phone)
                    return records
        except (OSError, json.JSONDecodeError, KeyError) as e:
            print(f"Error loading data: {e}")
            return []
        
class FileHandler:
    def __init__(self, file_path):
        self.file_path = file_path

    def save_data(self, records):
        with open(self.file_path, "w") as file:
            data = {
                "records": [record.__json__() for record in records]
            }
            json.dump(data, file)

    def load_data(self):
        try:
            if os.path.getsize(self.file_path) > 0:  
                with open(self.file_path, "r") as file:
                    data = json.load(file)
                    records = [Record(record["name"], record.get("birthday")) for record in data.get("records", [])]
                    for i, record in enumerate(records):
                        if "phones" in data.get("records", [])[i]:
                            for phone in data["records"][i]["phones"]:
                                record.add_phone(phone)
                    return records
        except (OSError, json.JSONDecodeError, KeyError) as e:
            print(f"Error loading data: {e}")
            return []


class ContactAssistant:
    def __init__(self, file_handler, address_book):
        self.file_handler = file_handler
        self.address_book = address_book

        if os.path.exists(self.file_handler.file_path):
            self.load_data()

    def load_data(self):
        records = self.file_handler.load_data()
        for record in records:
            self.address_book.add_record(record)

    def save_data(self):
        self.file_handler.save_data(self.address_book.values())

    def add_contact(self, name, phone, birthday=None):
        try:
            record = Record(name, birthday)
            record.add_phone(str(phone).strip()) 
            self.address_book.add_record(record)
            self.save_data()
            return f"Contact {name} added with phone {phone}"
        except ValueError as e:
            raise InputError(str(e))

    def change_contact(self, name, phone):
        try:
            record = self.address_book.find(name)
            if record:
                record.phones = []  
                record.add_phone(phone)
                self.save_data()  
                return f"Phone number for {name} changed to {phone}"
            else:
                raise IndexError
        except (ValueError, IndexError) as e:
            raise InputError(str(e))
        
    def get_phone(self, name):
        try:
            record = self.address_book.find(name)
            if record:
                return f"The phone number for {name} is {record.phones[0]}"
            else:
                raise IndexError
        except (ValueError, IndexError) as e:
            raise InputError(str(e))

    def show_all_contacts(self):
        records = list(self.address_book.values())
        if not records:
            return "No contacts found"
        else:
            result = "All contacts:\n"
            for record in records:
                phone_numbers = ', '.join(str(phone) for phone in record.phones)
                result += f"{record.name}: {phone_numbers}\n"
            return result.strip()


class CommandHandler:
    def __init__(self, contact_assistant):
        self.contact_assistant = contact_assistant

    def handle_hello(self, args):
        return "How can I help you?"

    def handle_add(self, args):
        if len(args) == 0:
            raise InputError("Invalid command. Please try again. Use 'add <name> <phone>'")

        contact_info = args.split(" ")
        if len(contact_info) != 3:
            raise InputError("Invalid command. Please try again. Use 'add <name> <phone>'")

        _, name, phone = args.split(" ")
        return self.contact_assistant.add_contact(name, phone)

    def handle_change(self, args):
        if len(args) == 0:
            raise InputError("Invalid command. Please try again. Use 'change <name> <phone>'")

        contact_info = args.split(" ")
        if len(contact_info) != 3:
            raise InputError("Invalid command. Please try again. Use 'add <name> <phone>'")

        _, name, phone = args.split(" ")
        return self.contact_assistant.change_contact(name, phone)

    def handle_phone(self, args):
        if len(args) == 0:
            raise InputError("Invalid command. Please try again. Use 'phone <name>'")
        args_list = args.split(" ")
        name = args_list[1]
        return self.contact_assistant.get_phone(name)

    def handle_show(self, args):
        return self.contact_assistant.show_all_contacts()

    def handle_bye(self, args):
        print("Good bye!")
        return None
    
    def handle_search(self, args):
        if len(args) == 0:
            raise InputError("Invalid command. Please try again. Use 'search <query>'")

        query = args.split(" ", 1)[1]
        matching_records = self.contact_assistant.address_book.search(query)

        if not matching_records:
            return "No matching contacts found"
        else:
            result = "Matching contacts:\n"
            for record in matching_records:
                phone_numbers = ', '.join(str(phone) for phone in record.phones)
                result += f"{record.name}: {phone_numbers}\n"
            return result.strip()

    def choice_action(self, data):
        actions = {
            'hello': self.handle_hello,
            'add': self.handle_add,
            "change": self.handle_change,
            "phone": self.handle_phone,
            'search': self.handle_search,
            "show": self.handle_show,
            "close": self.handle_bye,
            "exit": self.handle_bye,
            "good bye": self.handle_bye,
        }
        return actions.get(data, lambda args: "Invalid command")

    def process_input(self, user_input):
        try:
            if not user_input:
                raise InputError("Invalid command. Please try again.")

            space_index = user_input.find(' ')

            if space_index != -1:
                first_word = user_input[:space_index]
            else:
                first_word = user_input

            if first_word in ["good", "bye"]:
                first_word = "good bye"

            func = self.choice_action(first_word)
            result = func(user_input)

            if result is None:
                return None
            else:
                return result
        except InputError as e:
            return str(e)


def main():
    file_path = "address_book.json"
    data_handler = DataHandler(file_path)
    address_book = AddressBook()
    contact_assistant = ContactAssistant(data_handler, address_book)
    command_handler = CommandHandler(contact_assistant)

    while True:
        try:
            user_input = input("Enter command: ").lower().strip()
            result = command_handler.process_input(user_input)

            if result is None:
                break
            else:
                print(result)

        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()

    name = Name("John")
    print(name)  # Убедитесь, что выводит "John
