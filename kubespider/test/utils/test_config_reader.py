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
        os.mkdir("./test/tmp")

    def tearDown(self) -> None:
        # delete the test file
        with open(self.test_file, mode="w") as f:
            f.write(self.default_content)
        self.remove_files_and_dirs("./test/tmp")
        return super().tearDown()

    def remove_files_and_dirs(self, path):
        for root, dirs, files in os.walk(path, topdown=False):
          for file in files:
              os.remove(os.path.join(root, file))
          for dir in dirs:
              os.rmdir(os.path.join(root, dir))
        os.rmdir(path)

    
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

    def test_load_from_non_exist_file(self):
        # it is ok to load config from file not existing
        reader = YamlFileConfigReader("./test/tmp/test.yaml")
        data = reader.read()
        self.assertEqual(data, {})
        reader.parcial_update(lambda data: data.update({"version": 1}))
        self.assertEqual(reader.read(), {"version": 1})
