"""
Tests onnxml LabelEncoder converter
"""
import unittest
import warnings

import numpy as np
from sklearn.preprocessing import LabelEncoder
import torch

from hummingbird.ml._utils import onnx_ml_tools_installed, onnx_runtime_installed, lightgbm_installed
from hummingbird.ml import convert

if onnx_ml_tools_installed():
    from onnxmltools import convert_sklearn
    from onnxmltools.convert.common.data_types import Int32TensorType as IntTensorType_onnx
    from onnxmltools.convert.common.data_types import Int64TensorType as LongTensorType_onnx
    from onnxmltools.convert.common.data_types import StringTensorType as StringTensorType_onnx
    from onnxmltools.convert.common.data_types import FloatTensorType as FloatTensorType_onnx

if onnx_runtime_installed():
    import onnxruntime as ort


class TestONNXLabelEncoder(unittest.TestCase):

    # Test LabelEncoder with ints
    @unittest.skipIf(
        not (onnx_ml_tools_installed() and onnx_runtime_installed()), reason="ONNXML test requires ONNX, ORT and ONNXMLTOOLS"
    )
    def test_model_label_encoder_int_onnxml(self):
        model = LabelEncoder()
        data = np.array([1, 4, 5, 2, 0, 2], dtype=np.int32)
        model.fit(data)

        # Create ONNX-ML model
        onnx_ml_model = convert_sklearn(model, initial_types=[("int_input", LongTensorType_onnx(data.shape))])

        # Create ONNX model by calling converter
        onnx_model = convert(onnx_ml_model, "onnx", data)

        # Get the predictions for the ONNX-ML model
        session = ort.InferenceSession(onnx_ml_model.SerializeToString())
        output_names = [session.get_outputs()[i].name for i in range(len(session.get_outputs()))]
        inputs = {session.get_inputs()[0].name: X}
        onnx_ml_pred = session.run(output_names, inputs)

        # Get the predictions for the ONNX model
        onnx_pred = onnx_model.transform(X)

        # Check that predicted values match
        np.testing.assert_allclose(onnx_ml_pred, onnx_pred, rtol=rtol, atol=atol)

    # # Test LabelEncoder with ints
    # @unittest.skipIf(
    #     not (onnx_ml_tools_installed() and onnx_runtime_installed()), reason="ONNXML test requires ONNX, ORT and ONNXMLTOOLS"
    # )
    # def _test_model_label_encoder_str_onnxml(self):
    #     onnx_ml_model = LabelEncoder()
    #     #data = ['a', 'r', 'x', 'a']
    #     data = ["paris", "tokyo", "amsterdam", "tokyo",]
    #     onnx_ml_model.fit(data)

    #     # max word length is the smallest number which is divisible by 4 and larger than or equal to the length of any word
    #     max_word_length = 4
    #     num_columns = 4
    #     pytorch_input = torch.from_numpy(np.array(data, dtype='|S'+str(max_word_length)).view(np.int32)).view(-1, num_columns, max_word_length // 4)

    #     onnx_model = convert(onnx_ml_model, "onnx", data)

    #     pytorch_input = np.array(data, dtype='|S'+str(max_word_length)).view(np.int32).reshape(-1, num_columns, max_word_length // 4)

    #     # Create ONNX model by calling converter
    #     onnx_model = convert(onnx_ml_model, "onnx", pytorch_input)

    #     # Get the predictions for the ONNX-ML model
    #     session = ort.InferenceSession(onnx_ml_model.SerializeToString())
    #     output_names = [session.get_outputs()[i].name for i in range(len(session.get_outputs()))]
    #     inputs = {session.get_inputs()[0].name: data}
    #     onnx_ml_pred = session.run(output_names, inputs)

    #     # Get the predictions for the ONNX model
    #     session = ort.InferenceSession(onnx_model.SerializeToString())
    #     inputs_pyt = {session.get_inputs()[0].name: pytorch_input}
    #     onnx_pred = session.run(output_names, inputs_pyt)

    #     return onnx_ml_pred, onnx_pred

if __name__ == "__main__":
    unittest.main()
