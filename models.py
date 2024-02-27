from datetime import datetime
from collections import UserDict
from abc import ABC, abstractmethod

class Field(ABC):
    def __init__(self, value=""):
        self.__value = ""
        self.value = value

    @abstractmethod
    def is_valid(self, value):
        pass

    @property
    @abstractmethod
    def value(self):
        pass

    @value.setter
    @abstractmethod
    def value(self, new_value):
        pass

    @abstractmethod
    def __json__(self):
        pass

    def __str__(self):
        return str(self.value)

class StringField(Field):
    def __init__(self, value=""):
        super().__init__(value)
        self.__value = ""

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        if not self.is_valid(new_value):
            raise ValueError(f"Invalid value for {self.__class__.__name__.lower()}")
        self.__value = new_value

    def __json__(self):
        return self.value

class DateField(Field):
    def is_valid(self, value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        if not self.is_valid(new_value):
            raise ValueError(f"Invalid value for {self.__class__.__name__.lower()}")
        self.__value = new_value

    def __json__(self):
        return self.value

class Name(StringField):
    def __init__(self, value=""):
        super().__init__(value)

    def is_valid(self, value):
        return isinstance(value, str)

    def __json__(self):
        return self.value 

    def __str__(self):
        return self.value 

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        if not self.is_valid(new_value):
            raise ValueError(f"Invalid value for {self.__class__.__name__.lower()}")
        self.__value = new_value   

class Phone(StringField):
    def is_valid(self, value):
        return isinstance(value, str) and (len(value) == 10 or value.isdigit())

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        if not self.is_valid(new_value):
            raise ValueError(f"Invalid phone number format for '{new_value}'. It should be a 10-digit number.")
        self.__value = new_value

    def __json__(self):
        return str(self.value)
    
    def __str__(self):
        return self.value

class RecordSearch:
    @staticmethod
    def search_record(record, query):
        return (
            isinstance(record.name, StringField) and
            query.lower() in record.name.value.lower() or
            any(query in str(phone.value) for phone in record.phones)
        )

class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = DateField(birthday) if birthday else None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        initial_len = len(self.phones)
        self.phones = [p for p in self.phones if p.value != phone]
        if len(self.phones) == initial_len:
            raise ValueError(f"Phone number '{phone}' not found")

    def edit_phone(self, old_phone, new_phone):
        if not Phone(new_phone).is_valid(new_phone):
            raise ValueError(f"Invalid phone number format for '{new_phone}'")
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                return
        raise ValueError(f"Phone number '{old_phone}' not found")

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.now().date()
            birthday_date = datetime.strptime(self.birthday.value, "%Y-%m-%d").date()

            next_birthday = datetime(today.year, birthday_date.month, birthday_date.day).date()
            if today > next_birthday:
                next_birthday = datetime(today.year + 1, birthday_date.month, birthday_date.day).date()

            days_left = (next_birthday - today).days
            return days_left
        else:
            return None

    def __json__(self):
        record_data = {
            "name": self.name.__json__(),
            "phones": [phone.__json__() for phone in self.phones],
            "birthday": self.birthday.__json__() if self.birthday else None
        }
        return record_data

    def __str__(self):
        name_str = self.name.__str__()  
        phone_str = ', '.join(str(phone) for phone in self.phones)
        return f"{name_str}: {phone_str}"

class AddressBook(UserDict):
    def __init__(self, *args, **kwargs):
        self.data = {}
        super().__init__(*args, **kwargs)

    def search(self, query):
        return [record for record in self.data.values() if RecordSearch.search_record(record, query)]

    def add_record(self, record):
        self.data[record.name.value] = record

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def iterator(self, page_size=10):
        keys = list(self.data.keys())
        for i in range(0, len(keys), page_size):
            yield [self.data[key] for key in keys[i:i + page_size]]

    def find(self, name):
        return self.data.get(name)
