import unittest
import app
import os
import tempfile
import zipfile

class TestAppMethods(unittest.TestCase):
    def test_get_m2_path(self):
        # Testing if the .m2 path is correctly constructed
        expected_path = os.path.join(os.path.expanduser('~'), '.m2', 'repository')
        self.assertEqual(app.get_m2_path(), expected_path)

    def test_check_m2_repository(self):
        # This test might require setting up a mock .m2 repository
        with tempfile.TemporaryDirectory() as tempdir:
            original_m2_path = app.get_m2_path
            app.get_m2_path = lambda: tempdir  # Mocking the .m2 path
            # Add a mock JAR file
            jar_path = os.path.join(tempdir, 'test.jar')
            with open(jar_path, 'w') as f:
                f.write('')

            libraries = app.check_m2_repository()
            self.assertIn(jar_path, libraries)

            app.get_m2_path = original_m2_path  # Reset the path

    def test_get_jar_contents(self):
        # Create a temporary JAR file with some .class files
        with tempfile.NamedTemporaryFile(suffix='.jar', delete=False) as tempjar:
            tempjar.close()  # Close the file to release the lock in Windows

        try:
            with zipfile.ZipFile(tempjar.name, 'w') as jar:
                jar.writestr('Test.class', 'class content')
                jar.writestr('AnotherTest.class', 'class content')

            contents = app.get_jar_contents(tempjar.name)
            self.assertIn('Test.class', contents)
            self.assertIn('AnotherTest.class', contents)
        finally:
            os.remove(tempjar.name)  # Clean up the temporary file


if __name__ == '__main__':
    unittest.main()
