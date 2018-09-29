import unittest
import scorelib


class TestHelpingMethods(unittest.TestCase):

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

    def test_getPersonFromString(self):
        person = scorelib.getPersonFromString("Purcell, Henry (1659-1695)")
        self.assertEqual(person.name, "Purcell, Henry")
        self.assertEqual(person.born, 1659)
        self.assertEqual(person.died, 1695)

    def test_getPersonFromString2(self):
        person = scorelib.getPersonFromString("Purcell, Henry")
        self.assertEqual(person.name, "Purcell, Henry")
        self.assertIsNone(person.born)
        self.assertIsNone(person.died)

    def test_getPersonFromString3(self):
        person = scorelib.getPersonFromString("Purcell, Henry (1965)")
        self.assertEqual(person.name, "Purcell, Henry (1965)")
        self.assertIsNone(person.born)
        self.assertIsNone(person.died)

    def test_splitKeyAndValue(self):
        (key, value) = scorelib.splitKeyAndValue("someKey: someValue")
        self.assertEqual(key, "someKey")
        self.assertEqual(value, "someValue")

    def test_splitKeyAndValue2(self):
        (key, value) = scorelib.splitKeyAndValue("someKey: ")
        self.assertIsNone(key)
        self.assertIsNone(value)


if __name__ == '__main__':
    unittest.main()
