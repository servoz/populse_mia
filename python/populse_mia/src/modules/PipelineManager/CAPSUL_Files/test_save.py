import os
import json
import shutil
import unittest
import tempfile
import datetime

from capsul.api import Process, Pipeline
from traits.api import Float, File, String, Int, List, TraitListObject


class TestInt(Process):

    def __init__(self):
        super(TestInt, self).__init__()

        self.add_trait("in_1", Int(output=False))
        self.add_trait("in_2", Int(output=False))
        self.add_trait("out", Int(output=True))

    def _run_process(self):
        self.out = self.in_1 + self.in_2
        print('TestInt\n...\nInputs: {', self.in_1, ', ',
              self.in_2, '}\nOutput: ', self.out, '\n...\n')


class TestFloat(Process):

    def __init__(self):
        super(TestFloat, self).__init__()

        self.add_trait("in_1", Float(output=False))
        self.add_trait("in_2", Float(output=False))
        self.add_trait("out", Float(output=True))

    def _run_process(self):
        self.out = self.in_1 - self.in_2
        print('TestFloat\n...\nInputs: {', self.in_1, ', ',
              self.in_2, '}\nOutput: ', self.out, '\n...\n')


class TestString(Process):

    def __init__(self):
        super(TestString, self).__init__()

        self.add_trait("in_1", String(output=False))
        self.add_trait("in_2", String(output=False))
        self.add_trait("out", String(output=True))

    def _run_process(self):
        self.out = self.in_1 + self.in_2
        print('TestString\n...\nInputs: {', self.in_1, ', ',
              self.in_2, '}\nOutput: ', self.out, '\n...\n')


class TestFile(Process):

    def __init__(self):
        super(TestFile, self).__init__()

        self.add_trait("in_1", File(output=False))
        self.add_trait("in_2", File(output=False))
        self.add_trait("out", List(File(), output=True))

    def _run_process(self):
        self.out = [self.in_1, self.in_2]
        print('TestFile\n...\nInputs: {', self.in_1, ', ',
              self.in_2, '}\nOutput: ', self.out, '\n...\n')


class TestListInt(Process):

    def __init__(self):
        super(TestListInt, self).__init__()

        self.add_trait("in_1", List(Int(), output=False))
        self.add_trait("in_2", List(Int(), output=False))
        self.add_trait("out", List(Int(), output=True))

    def _run_process(self):
        l = []
        for idx, i in enumerate(self.in_1):
            l.append(i + self.in_2[idx])
        self.out = l

        print('TestListInt\n...\nInputs: {', self.in_1, ', ',
              self.in_2, '}\nOutput: ', self.out, '\n...\n')


class TestListFloat(Process):

    def __init__(self):
        super(TestListFloat, self).__init__()

        self.add_trait("in_1", List(Float(), output=False))
        self.add_trait("in_2", List(Float(), output=False))
        self.add_trait("out", List(Float(), output=True))

    def _run_process(self):
        l = []
        for idx, i in enumerate(self.in_1):
            l.append(i - self.in_2[idx])
        self.out = l

        print('TestListFloat\n...\nInputs: {', self.in_1, ', ',
              self.in_2, '}\nOutput: ', self.out, '\n...\n')


class TestListString(Process):

    def __init__(self):
        super(TestListString, self).__init__()

        self.add_trait("in_1", List(String(), output=False))
        self.add_trait("in_2", List(String(), output=False))
        self.add_trait("out", List(String(), output=True))

    def _run_process(self):
        l = []
        for idx, i in enumerate(self.in_1):
            l.append(i + self.in_2[idx])
        self.out = l

        print('TestListString\n...\nInputs: {', self.in_1, ', ',
              self.in_2, '}\nOutput: ', self.out, '\n...\n')


class TestListFile(Process):

    def __init__(self):
        super(TestListFile, self).__init__()

        self.add_trait("in_1", List(File(), output=False))
        self.add_trait("in_2", List(File(), output=False))
        self.add_trait("out", List(File(), output=True))

    def _run_process(self):
        self.out = [self.in_1[0], self.in_2[0]]
        print('TestListFile\n...\nInputs: {', self.in_1, ', ',
              self.in_2, '}\nOutput: ', self.out, '\n...\n')


class TestListList(Process):

    def __init__(self):
        super(TestListList, self).__init__()

        self.add_trait("in_1", List(List(Int()), output=False))
        self.add_trait("in_2", List(List(Int()), output=False))
        self.add_trait("out", List(List(Int()), output=True))

    def _run_process(self):
        l = []
        for idx, i in enumerate(self.in_1):
            l.append(i[0] + self.in_2[idx][0])
        self.out = l

        print('TestListList\n...\nInputs: {', self.in_1, ', ',
              self.in_2, '}\nOutput: ', self.out, '\n...\n')


def load_pipeline_parameters(filename, pipeline):
    """
    Loading and setting pipeline parameters (inputs and outputs) from a Json file.
    :return:
    """

    if filename:
        with open(filename, 'r', encoding='utf8') as file:
            dic = json.load(file)

        if "pipeline_parameters" not in dic.keys():
            raise KeyError('No "pipeline_parameters" key found in {0}.'.format(filename))

        for trait_name, trait_value in dic["pipeline_parameters"].items():
            if trait_name not in pipeline.user_traits().keys():
                # Should we raise an error or just "continue"?
                raise KeyError('No "{0}" parameter in pipeline.'.format(trait_name))
            setattr(pipeline, trait_name, trait_value)
        pipeline.update_nodes_and_plugs_activation()


def load_pipeline_dictionary(filename):
    if filename:
        with open(filename, 'r', encoding='utf8') as file:
            dic = json.load(file)
        return dic


def save_pipeline_parameters(filename, pipeline):
    """
    Saving pipeline parameters (inputs and outputs) to a Json file.
    :return:
    """

    if filename:
        from traits.api import Undefined
        # Generating the dictionary
        param_dic = {}
        for trait_name, trait in pipeline.user_traits().items():
            if trait_name in ["nodes_activation"]:
                continue
            value = getattr(pipeline, trait_name)
            if value is Undefined:
                value = ""
            param_dic[trait_name] = value

        # In the future, more information may be added to this dictionary
        dic = {}
        dic["pipeline_parameters"] = param_dic

        # Saving the dictionary in the Json file
        with open(filename, 'w', encoding='utf8') as file:
            json.dump(dic, file)


class TestPipelineMethods(unittest.TestCase):
    """
    Class executing the unit tests of load_pipeline_parameters and save_pipeline_parameters
    """

    def setUp(self):
        """
        Called before every unit test
        Creates a temporary folder containing the database file that will be used for the test
        """

        self.temp_folder = tempfile.mkdtemp()
        self.path = os.path.join(self.temp_folder, "test.json")

    def tearDown(self):
        """
        Called after every unit test
        Deletes the temporary folder created for the test
        """

        shutil.rmtree(self.temp_folder)

    def test_int(self):
        class Pipeline1(Pipeline):

            def pipeline_definition(self):
                # Create processes
                self.add_process("node_1", TestInt())
                # Exports
                self.export_parameter("node_1", "in_1", "in_1")
                self.export_parameter("node_1", "in_2", "in_2")
                self.export_parameter("node_1", "out", "out")

        in_1 = 2
        in_2 = 4
        out = 6

        pipeline1 = Pipeline1()
        pipeline1.in_1 = in_1
        pipeline1.in_2 = in_2
        pipeline1()

        save_pipeline_parameters(self.path, pipeline1)

        # Reinitializing pipeline and loading parameters
        pipeline1 = Pipeline1()
        load_pipeline_parameters(self.path, pipeline1)
        self.assertEqual(pipeline1.in_1, in_1)
        self.assertEqual(pipeline1.in_2, in_2)
        self.assertEqual(pipeline1.out, out)

        self.assertEqual(type(pipeline1.in_1), int)
        self.assertEqual(type(pipeline1.in_2), int)
        self.assertEqual(type(pipeline1.out), int)

        # Verifying the dictionary
        dic = load_pipeline_dictionary(self.path)
        self.assertEqual(dic["pipeline_parameters"]["in_1"], in_1)
        self.assertEqual(dic["pipeline_parameters"]["in_2"], in_2)
        self.assertEqual(dic["pipeline_parameters"]["out"], out)

        self.assertEqual(type(dic["pipeline_parameters"]["in_1"]), int)
        self.assertEqual(type(dic["pipeline_parameters"]["in_2"]), int)
        self.assertEqual(type(dic["pipeline_parameters"]["out"]), int)

    def test_float(self):
        class Pipeline1(Pipeline):

            def pipeline_definition(self):
                # Create processes
                self.add_process("node_1", TestFloat())
                # Exports
                self.export_parameter("node_1", "in_1", "in_1")
                self.export_parameter("node_1", "in_2", "in_2")
                self.export_parameter("node_1", "out", "out")

        pipeline1 = Pipeline1()
        pipeline1.in_1 = 2.0
        pipeline1.in_2 = 4.0
        pipeline1()

        in_1 = 2.0
        in_2 = 4.0
        out = -2.0

        pipeline1 = Pipeline1()
        pipeline1.in_1 = in_1
        pipeline1.in_2 = in_2
        pipeline1()

        save_pipeline_parameters(self.path, pipeline1)

        # Reinitializing pipeline and loading parameters
        pipeline1 = Pipeline1()
        load_pipeline_parameters(self.path, pipeline1)
        self.assertEqual(pipeline1.in_1, in_1)
        self.assertEqual(pipeline1.in_2, in_2)
        self.assertEqual(pipeline1.out, out)

        self.assertEqual(type(pipeline1.in_1), float)
        self.assertEqual(type(pipeline1.in_2), float)
        self.assertEqual(type(pipeline1.out), float)

        # Verifying the dictionary
        dic = load_pipeline_dictionary(self.path)
        self.assertEqual(dic["pipeline_parameters"]["in_1"], in_1)
        self.assertEqual(dic["pipeline_parameters"]["in_2"], in_2)
        self.assertEqual(dic["pipeline_parameters"]["out"], out)

        self.assertEqual(type(dic["pipeline_parameters"]["in_1"]), float)
        self.assertEqual(type(dic["pipeline_parameters"]["in_2"]), float)
        self.assertEqual(type(dic["pipeline_parameters"]["out"]), float)

    def test_string(self):
        class Pipeline1(Pipeline):

            def pipeline_definition(self):
                # Create processes
                self.add_process("node_1", TestString())
                # Exports
                self.export_parameter("node_1", "in_1", "in_1")
                self.export_parameter("node_1", "in_2", "in_2")
                self.export_parameter("node_1", "out", "out")

        in_1 = "This is "
        in_2 = "a test"
        out = "This is " + "a test"

        pipeline1 = Pipeline1()
        pipeline1.in_1 = in_1
        pipeline1.in_2 = in_2
        pipeline1()

        save_pipeline_parameters(self.path, pipeline1)

        # Reinitializing pipeline and loading parameters
        pipeline1 = Pipeline1()
        load_pipeline_parameters(self.path, pipeline1)
        self.assertEqual(pipeline1.in_1, in_1)
        self.assertEqual(pipeline1.in_2, in_2)
        self.assertEqual(pipeline1.out, out)

        self.assertEqual(type(pipeline1.in_1), str)
        self.assertEqual(type(pipeline1.in_2), str)
        self.assertEqual(type(pipeline1.out), str)

        # Verifying the dictionary
        dic = load_pipeline_dictionary(self.path)
        self.assertEqual(dic["pipeline_parameters"]["in_1"], in_1)
        self.assertEqual(dic["pipeline_parameters"]["in_2"], in_2)
        self.assertEqual(dic["pipeline_parameters"]["out"], out)

        self.assertEqual(type(dic["pipeline_parameters"]["in_1"]), str)
        self.assertEqual(type(dic["pipeline_parameters"]["in_2"]), str)
        self.assertEqual(type(dic["pipeline_parameters"]["out"]), str)

    def test_file(self):
        class Pipeline1(Pipeline):

            def pipeline_definition(self):
                # Create processes
                self.add_process("node_1", TestFile())
                # Exports
                self.export_parameter("node_1", "in_1", "in_1")
                self.export_parameter("node_1", "in_2", "in_2")
                self.export_parameter("node_1", "out", "out")

        in_1 = '/tmp/yolo.nii'
        in_2 = '/tmp/yolo2.nii'
        out = ['/tmp/yolo.nii', '/tmp/yolo2.nii']

        pipeline1 = Pipeline1()
        pipeline1.in_1 = in_1
        pipeline1.in_2 = in_2
        pipeline1()

        save_pipeline_parameters(self.path, pipeline1)

        # Reinitializing pipeline and loading parameters
        pipeline1 = Pipeline1()
        load_pipeline_parameters(self.path, pipeline1)
        self.assertEqual(pipeline1.in_1, in_1)
        self.assertEqual(pipeline1.in_2, in_2)
        self.assertEqual(pipeline1.out, out)

        self.assertEqual(type(pipeline1.in_1), str)
        self.assertEqual(type(pipeline1.in_2), str)
        self.assertEqual(type(pipeline1.out), TraitListObject)

        for idx, element in enumerate(pipeline1.out):
            self.assertEqual(element, out[idx])
            self.assertEqual(type(element), str)

        # Verifying the dictionary
        dic = load_pipeline_dictionary(self.path)
        self.assertEqual(dic["pipeline_parameters"]["in_1"], in_1)
        self.assertEqual(dic["pipeline_parameters"]["in_2"], in_2)
        self.assertEqual(dic["pipeline_parameters"]["out"], out)

        self.assertEqual(type(dic["pipeline_parameters"]["in_1"]), str)
        self.assertEqual(type(dic["pipeline_parameters"]["in_2"]), str)
        self.assertEqual(type(dic["pipeline_parameters"]["out"]), list)

    def test_list_int(self):
        class Pipeline1(Pipeline):

            def pipeline_definition(self):
                # Create processes
                self.add_process("node_1", TestListInt())
                # Exports
                self.export_parameter("node_1", "in_1", "in_1")
                self.export_parameter("node_1", "in_2", "in_2")
                self.export_parameter("node_1", "out", "out")

        in_1 = [2, 4, 5]
        in_2 = [4, 8, 9]
        out = [6, 12, 14]

        pipeline1 = Pipeline1()
        pipeline1.in_1 = in_1
        pipeline1.in_2 = in_2
        pipeline1()

        save_pipeline_parameters(self.path, pipeline1)

        # Reinitializing pipeline and loading parameters
        pipeline1 = Pipeline1()
        load_pipeline_parameters(self.path, pipeline1)
        self.assertEqual(pipeline1.in_1, in_1)
        self.assertEqual(pipeline1.in_2, in_2)
        self.assertEqual(pipeline1.out, out)

        self.assertEqual(type(pipeline1.in_1), TraitListObject)
        self.assertEqual(type(pipeline1.in_2), TraitListObject)
        self.assertEqual(type(pipeline1.out), TraitListObject)

        for idx, element in enumerate(pipeline1.in_1):
            self.assertEqual(element, in_1[idx])
            self.assertEqual(type(element), int)

        for idx, element in enumerate(pipeline1.in_2):
            self.assertEqual(element, in_2[idx])
            self.assertEqual(type(element), int)

        for idx, element in enumerate(pipeline1.out):
            self.assertEqual(element, out[idx])
            self.assertEqual(type(element), int)

        # Verifying the dictionary
        dic = load_pipeline_dictionary(self.path)
        self.assertEqual(dic["pipeline_parameters"]["in_1"], in_1)
        self.assertEqual(dic["pipeline_parameters"]["in_2"], in_2)
        self.assertEqual(dic["pipeline_parameters"]["out"], out)

        self.assertEqual(type(dic["pipeline_parameters"]["in_1"]), list)
        self.assertEqual(type(dic["pipeline_parameters"]["in_2"]), list)
        self.assertEqual(type(dic["pipeline_parameters"]["out"]), list)

        for idx, element in enumerate(dic["pipeline_parameters"]["in_1"]):
            self.assertEqual(element, in_1[idx])
            self.assertEqual(type(element), int)

        for idx, element in enumerate(dic["pipeline_parameters"]["in_2"]):
            self.assertEqual(element, in_2[idx])
            self.assertEqual(type(element), int)

        for idx, element in enumerate(dic["pipeline_parameters"]["out"]):
            self.assertEqual(element, out[idx])
            self.assertEqual(type(element), int)

    def test_list_float(self):
        class Pipeline1(Pipeline):

            def pipeline_definition(self):
                # Create processes
                self.add_process("node_1", TestListFloat())
                # Exports
                self.export_parameter("node_1", "in_1", "in_1")
                self.export_parameter("node_1", "in_2", "in_2")
                self.export_parameter("node_1", "out", "out")

        in_1 = [2.0, 4.0, 5.0]
        in_2 = [4.0, 8.0, 9.0]
        out = [-2.0, -4.0, -4.0]

        pipeline1 = Pipeline1()
        pipeline1.in_1 = in_1
        pipeline1.in_2 = in_2
        pipeline1()

        save_pipeline_parameters(self.path, pipeline1)

        # Reinitializing pipeline and loading parameters
        pipeline1 = Pipeline1()
        load_pipeline_parameters(self.path, pipeline1)
        self.assertEqual(pipeline1.in_1, in_1)
        self.assertEqual(pipeline1.in_2, in_2)
        self.assertEqual(pipeline1.out, out)

        self.assertEqual(type(pipeline1.in_1), TraitListObject)
        self.assertEqual(type(pipeline1.in_2), TraitListObject)
        self.assertEqual(type(pipeline1.out), TraitListObject)

        for idx, element in enumerate(pipeline1.in_1):
            self.assertEqual(element, in_1[idx])
            self.assertEqual(type(element), float)

        for idx, element in enumerate(pipeline1.in_2):
            self.assertEqual(element, in_2[idx])
            self.assertEqual(type(element), float)

        for idx, element in enumerate(pipeline1.out):
            self.assertEqual(element, out[idx])
            self.assertEqual(type(element), float)

        # Verifying the dictionary
        dic = load_pipeline_dictionary(self.path)
        self.assertEqual(dic["pipeline_parameters"]["in_1"], in_1)
        self.assertEqual(dic["pipeline_parameters"]["in_2"], in_2)
        self.assertEqual(dic["pipeline_parameters"]["out"], out)

        self.assertEqual(type(dic["pipeline_parameters"]["in_1"]), list)
        self.assertEqual(type(dic["pipeline_parameters"]["in_2"]), list)
        self.assertEqual(type(dic["pipeline_parameters"]["out"]), list)

        for idx, element in enumerate(dic["pipeline_parameters"]["in_1"]):
            self.assertEqual(element, in_1[idx])
            self.assertEqual(type(element), float)

        for idx, element in enumerate(dic["pipeline_parameters"]["in_2"]):
            self.assertEqual(element, in_2[idx])
            self.assertEqual(type(element), float)

        for idx, element in enumerate(dic["pipeline_parameters"]["out"]):
            self.assertEqual(element, out[idx])
            self.assertEqual(type(element), float)

    def test_list_string(self):
        class Pipeline1(Pipeline):

            def pipeline_definition(self):
                # Create processes
                self.add_process("node_1", TestListString())
                # Exports
                self.export_parameter("node_1", "in_1", "in_1")
                self.export_parameter("node_1", "in_2", "in_2")
                self.export_parameter("node_1", "out", "out")

        in_1 = ["hello ", "hey "]
        in_2 = ["salut", "coucou"]
        out = ["hello salut", "hey coucou"]

        pipeline1 = Pipeline1()
        pipeline1.in_1 = in_1
        pipeline1.in_2 = in_2
        pipeline1()

        save_pipeline_parameters(self.path, pipeline1)

        # Reinitializing pipeline and loading parameters
        pipeline1 = Pipeline1()
        load_pipeline_parameters(self.path, pipeline1)
        self.assertEqual(pipeline1.in_1, in_1)
        self.assertEqual(pipeline1.in_2, in_2)
        self.assertEqual(pipeline1.out, out)

        self.assertEqual(type(pipeline1.in_1), TraitListObject)
        self.assertEqual(type(pipeline1.in_2), TraitListObject)
        self.assertEqual(type(pipeline1.out), TraitListObject)

        for idx, element in enumerate(pipeline1.in_1):
            self.assertEqual(element, in_1[idx])
            self.assertEqual(type(element), str)

        for idx, element in enumerate(pipeline1.in_2):
            self.assertEqual(element, in_2[idx])
            self.assertEqual(type(element), str)

        for idx, element in enumerate(pipeline1.out):
            self.assertEqual(element, out[idx])
            self.assertEqual(type(element), str)

        # Verifying the dictionary
        dic = load_pipeline_dictionary(self.path)
        self.assertEqual(dic["pipeline_parameters"]["in_1"], in_1)
        self.assertEqual(dic["pipeline_parameters"]["in_2"], in_2)
        self.assertEqual(dic["pipeline_parameters"]["out"], out)

        self.assertEqual(type(dic["pipeline_parameters"]["in_1"]), list)
        self.assertEqual(type(dic["pipeline_parameters"]["in_2"]), list)
        self.assertEqual(type(dic["pipeline_parameters"]["out"]), list)

        for idx, element in enumerate(dic["pipeline_parameters"]["in_1"]):
            self.assertEqual(element, in_1[idx])
            self.assertEqual(type(element), str)

        for idx, element in enumerate(dic["pipeline_parameters"]["in_2"]):
            self.assertEqual(element, in_2[idx])
            self.assertEqual(type(element), str)

        for idx, element in enumerate(dic["pipeline_parameters"]["out"]):
            self.assertEqual(element, out[idx])
            self.assertEqual(type(element), str)

    def test_list_file(self):
        class Pipeline1(Pipeline):

            def pipeline_definition(self):
                # Create processes
                self.add_process("node_1", TestListFile())
                # Exports
                self.export_parameter("node_1", "in_1", "in_1")
                self.export_parameter("node_1", "in_2", "in_2")
                self.export_parameter("node_1", "out", "out")

        in_1 = ["/tmp/yolo.txt", "/tmp/yolo2.txt"]
        in_2 = ["/tmp/yolo.nii", "/tmp/yolo2.nii"]
        out = ["/tmp/yolo.txt", "/tmp/yolo.nii"]

        pipeline1 = Pipeline1()
        pipeline1.in_1 = in_1
        pipeline1.in_2 = in_2
        pipeline1()

        save_pipeline_parameters(self.path, pipeline1)

        # Reinitializing pipeline and loading parameters
        pipeline1 = Pipeline1()
        load_pipeline_parameters(self.path, pipeline1)
        self.assertEqual(pipeline1.in_1, in_1)
        self.assertEqual(pipeline1.in_2, in_2)
        self.assertEqual(pipeline1.out, out)

        self.assertEqual(type(pipeline1.in_1), TraitListObject)
        self.assertEqual(type(pipeline1.in_2), TraitListObject)
        self.assertEqual(type(pipeline1.out), TraitListObject)

        for idx, element in enumerate(pipeline1.in_1):
            self.assertEqual(element, in_1[idx])
            self.assertEqual(type(element), str)

        for idx, element in enumerate(pipeline1.in_2):
            self.assertEqual(element, in_2[idx])
            self.assertEqual(type(element), str)

        for idx, element in enumerate(pipeline1.out):
            self.assertEqual(element, out[idx])
            self.assertEqual(type(element), str)

        # Verifying the dictionary
        dic = load_pipeline_dictionary(self.path)
        self.assertEqual(dic["pipeline_parameters"]["in_1"], in_1)
        self.assertEqual(dic["pipeline_parameters"]["in_2"], in_2)
        self.assertEqual(dic["pipeline_parameters"]["out"], out)

        self.assertEqual(type(dic["pipeline_parameters"]["in_1"]), list)
        self.assertEqual(type(dic["pipeline_parameters"]["in_2"]), list)
        self.assertEqual(type(dic["pipeline_parameters"]["out"]), list)

        for idx, element in enumerate(dic["pipeline_parameters"]["in_1"]):
            self.assertEqual(element, in_1[idx])
            self.assertEqual(type(element), str)

        for idx, element in enumerate(dic["pipeline_parameters"]["in_2"]):
            self.assertEqual(element, in_2[idx])
            self.assertEqual(type(element), str)

        for idx, element in enumerate(dic["pipeline_parameters"]["out"]):
            self.assertEqual(element, out[idx])
            self.assertEqual(type(element), str)

    def test_list_list(self):
        pass
