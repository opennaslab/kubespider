import unittest
import yaml
import os
from utils.config_reader import YamlFileConfigReader, YamlFileSectionConfigReader

class TestConfigReader(unittest.TestCase):
    def setUp(self):
        # create a simple yaml file for test
        self.test_file = "./test/utils/test_config.yaml"
        with open(self.test_file, mode="r") as f:
            self.default_content = f.read()

    def tearDown(self) -> None:
        # delete the test file
        with open(self.test_file, mode="w") as f:
            f.write(self.default_content)
        return super().tearDown()
    
    def test_yaml_file_reader(self):
        reader = YamlFileConfigReader(self.test_file)
        data = reader.read()
        data["outer_key"] = "new_value"
        data["new_key"] = "a"
        reader.save(data)
        data = reader.read()
        self.assertEqual(data["new_key"], "a")
        self.assertEqual(data["outer_key"], "new_value")

    def test_yaml_section_reader(self):
        reader_one = YamlFileSectionConfigReader(self.test_file, "section_one")
        reader_one_data = reader_one.read()
        reader_two = YamlFileSectionConfigReader(self.test_file, "section_two")
        reader_two_data = reader_two.read()
        self.assertEqual(reader_one_data, {"version": 1})
        self.assertEqual(reader_two_data, {"version": 1})
        reader_one_data["version"] = 2
        reader_two_data["version"] = 3
        reader_one.save(reader_one_data)
        reader_two.save(reader_two_data)
        reader_one_data = reader_one.read()
        reader_two_data = reader_two.read()
        self.assertEqual(reader_one_data, {"version": 2})
        self.assertEqual(reader_two_data, {"version": 3})
