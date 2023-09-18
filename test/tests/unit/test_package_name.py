from unittest import TestCase

# Test class
from src.package_name import PackageName


class TestConfigLoader(TestCase):
    def test_init_returns_correct_instance_with_config_file(self):
        pkg = PackageName()

        # Asserts
        self.assertEqual(pkg.foo, "bar")
