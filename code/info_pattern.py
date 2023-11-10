from typing import Any
class paired_info_pattern_modified():

    def __init__(self):
        self.data = {}

    def setter(self, name: str, value: Any) -> None:
        if self.data.get(name) != None:
            return False
        self.data[name] = value
        return True

    def output(self):
        # result = {
        #     "user": self.user,
        #     "password": self.password,
        #     "address": self.address,
        #     "port": self.port,
        #     "phonenumber": self.phonenumber
        # }
        # remove None attributes
        result = {}
        for key in self.data:
            if self.data[key] != None:
                result[key] = self.data[key]
        # check if result have all needed attributes
        for key in ["user", "password", "address", "port", "phonenumber"]:
            if key not in result:
                result[key] = None
        self.__init__()
        return result

    def getter(self, name: str):
        if name in self.data:
            return self.data[name]
        else:
            return None

    def if_same_attr(self, name: str, value: Any) -> bool:

        # check if name is in self.data
        if self.data.get(name) == None:
            return False
        # print("self.data:"+str(self.data))
        # print("1if_same_attr: "+str(self.data.get(name)+" "+str(value)))
        return self.data.get(name) == value

    def is_None(self):
        # return self.data.get("user") == None and self.data.get("password") == None and self.data.get("address") == None and self.data.get("port") == None
        return self.data.get("user") == None and self.data.get("password") == None and self.data.get("address") == None and self.data.get("port") == None and self.data.get("phonenumber") == None



from typing import Any
class paired_info_pattern():

    def __init__(self):
        self.port = None
        self.address = None
        self.user = None
        self.password = None
        self.phonenumber = None

    def set_port(self, port):
        self.port = port

    def set_address(self, address):
        self.address = address

    def set_user(self, user):
        self.user = user

    def set_password(self, password):
        self.password = password

    def set_phonenumber(self, phonenumber):
        self.phonenumber = phonenumber

    def setter(self, name: str, value: Any) -> None:
        # if self.__dict__.get(name) != None and self.__dict__.get(name) != value:
        #     return False
        attr_switch = {
            "port": lambda x: self.set_port(x),
            "address": lambda x: self.set_address(x),
            "user": lambda x: self.set_user(x),
            "password": lambda x: self.set_password(x),
            "phonenumber": lambda x: self.set_phonenumber(x)
        }
        if name in attr_switch:
            # # print("Setting "+str(name)+" " +str( value))
            return attr_switch[name](value)
        else:
            return False

    def output(self):
        result = {
            "user": self.user,
            "password": self.password,
            "address": self.address,
            "port": self.port,
            "phonenumber": self.phonenumber
        }
        # remove None attributes
        
        self.__init__()
        return result

    def getter(self, name: str):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            return None

    def if_same_attr(self, name: str, value: Any) -> bool:
        return self.__dict__.get(name) == value

    def is_None(self):
        return self.__dict__.get("user") == None and self.__dict__.get("password") == None and self.__dict__.get("address") == None and self.__dict__.get("port") == None

# Create instances of both classes
original = paired_info_pattern()
modified = paired_info_pattern_modified()

# Test setting attributes
original.set_user("user1")
modified.setter("user", "user1")
original.set_password("pass1")
modified.setter("password", "pass1")

# Test if_same_attr method
# print(original.if_same_attr("user", "user1"))
# print(modified.if_same_attr("user", "user1"))
assert original.if_same_attr("user", "user1") == modified.if_same_attr("user", "user1")
assert original.if_same_attr("password", "pass1") == modified.if_same_attr("password", "pass1")

# Test output method
# print(original.output())
# print(modified.output())
assert original.output() == modified.output()

# Test is_None method
assert original.is_None() == modified.is_None()

# Reset the instances
original.__init__()
modified.__init__()

# Test if_same_attr method with different values
assert original.if_same_attr("user", "user1") == modified.if_same_attr("user", "user2")
assert original.if_same_attr("password", "pass1") == modified.if_same_attr("password", "pass2")

# Test output method with different values
assert original.output() == modified.output()

# Test is_None method with different values
assert original.is_None() == modified.is_None()

# print("Tests completed.")






import unittest
class TestPairedInfoPattern(unittest.TestCase):
    def setUp(self):
        # Create an instance of the paired_info_pattern class for testing
        self.info = paired_info_pattern_modified()

    def test_setters_and_getters(self):
        # Test setting and getting various attributes
        self.info.setter("user", "test_user")
        self.assertEqual(self.info.getter("user"), "test_user")

        self.info.setter("password", "test_password")
        self.assertEqual(self.info.getter("password"), "test_password")

        self.info.setter("address", "test_address")
        self.assertEqual(self.info.getter("address"), "test_address")

        self.info.setter("port", 8080)
        self.assertEqual(self.info.getter("port"), 8080)

        self.info.setter("phonenumber", "123-456-7890")
        self.assertEqual(self.info.getter("phonenumber"), "123-456-7890")

    def test_output_method(self):
        # Test the output method
        self.info.setter("user", "test_user")
        self.info.setter("password", "test_password")
        self.info.setter("address", "test_address")
        self.info.setter("port", 8080)
        self.info.setter("phonenumber", "123-456-7890")

        result = self.info.output()
        expected_result = {
            "user": "test_user",
            "password": "test_password",
            "address": "test_address",
            "port": 8080,
            "phonenumber": "123-456-7890"
        }
        self.assertEqual(result, expected_result)

    def test_if_same_attr_method(self):
        # Test if_same_attr method
        self.info.setter("user", "test_user")
        self.assertTrue(self.info.if_same_attr("user", "test_user"))
        self.assertFalse(self.info.if_same_attr("user", "different_user"))

    def test_is_None_method(self):
        # Test is_None method
        self.assertTrue(self.info.is_None())
        self.info.setter("user", "test_user")
        self.assertFalse(self.info.is_None())

if __name__ == '__main__':
    unittest.main()
