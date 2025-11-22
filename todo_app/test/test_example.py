import pytest


# Test whether 3 is equal to 3
def test_equal_or_not_equal():
    assert 3 == 3


# Test is instance
def test_is_instance():
    assert isinstance('This is a string', str)
    assert not isinstance('10', int)


# Test boolean
def test_boolean():
    validate = True
    assert validate is True
    assert ('hello' == 'world') is False


# Test type
def test_type():
    assert type('Hello' is str)
    assert type('World' is not int)


# Test greater and less than
def test_greater_and_less_than():
    assert 7 > 3
    assert 4 < 10


# Test list
def test_list():
    num_list = [1, 2, 3, 4, 5]
    any_list = [False, False]
    assert 1 in num_list
    assert 7 not in num_list
    assert all(num_list)


# Pytest object and Fixture
class Student:
    def __init__(self, first_name, last_name, major, years):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years


@pytest.fixture
def default_student():
    return Student('John', 'Doe', 'Computer Science', 3)


def test_student_initialization(default_student):
    assert default_student.first_name == 'John'
    assert default_student.last_name == 'Doe'
    assert default_student.major == 'Computer Science'
    assert default_student.years == 3
