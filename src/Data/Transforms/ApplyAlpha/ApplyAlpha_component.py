from typing import cast, Any, Optional, Dict, Tuple
from dneg_ml_toolkit.src.Data.Transforms.BASE_Transform.BASE_Transform_component import BASE_Transform
from dneg_ml_toolkit.src.Data.ml_toolkit_dictionary import MLToolkitDictionary
from dneg_ml_toolkit.src.Data.image_tools import image_dtype_utils

from src.Data.Transforms.MakeAlpha.MakeAlpha_config import MakeAlphaConfig

from PIL import Image, ImageDraw

import numpy as np


class ApplyAlpha(BASE_Transform):

    def __init__(self, config: MakeAlphaConfig):
        # The Transform will apply the data augmentation to any data specified in its configuration's
        # ApplyTo field.
        # It may specify an additional list of keys and pass it to the parent constructor as the
        # required_transform_metadata parameter. These data items will always be retrieved and are used
        # for calculating the augmentation to apply to the ApplyTo data. These metadata items will not
        # be altered by the Transform
        # This example just requests the dataset index for the piece of data
        required_transform_metadata = ["index", config.AlphaChannel]
        super().__init__(config, required_transform_metadata=required_transform_metadata)


    def apply_transform(self, data_key: str, data_to_transform: Any, transform_metadata: Optional[Dict[str, Any]]) \
            -> Tuple[Any, Optional[MLToolkitDictionary[Any]]]:
        """
        Apply the Transform to the data

        Args:
             data_key: The key that identifies the data
            data_to_transform: The piece of data to apply the transformation to
            transform_metadata: An optional dictionary of additional data gathered using the keys passed as
                required_transform_metadata in the constructor. This additional data does not get
                transformed, but can be used for the calculation and application of the transform
                to the data_to_transform.

        Returns:
            The transformed piece of data; an optional dictionary of additional data that will be added to the same
                dictionary that the transformed data is stored in, for cases where the Transform generates new data from
                the input data.
        """

        # 1. Get the data type of the input data (and the device if it is a tensor). These are tracked so that
        # the transformed data can be returned with the matching data type

        # format using the ML Toolkit's helper function
        data_to_transform, _ = image_dtype_utils.transform_data_type(data_to_transform,
                                                                     to_type=image_dtype_utils.ImageDataType.PILImage)

        #alpha is type "F" (float 0..1), convert to uint 8 in then to type "L" (8bit)
        alpha, _ = image_dtype_utils.transform_data_type(transform_metadata[self.config.AlphaChannel],
                                                         to_type=image_dtype_utils.ImageDataType.NPArray)
        alpha = (alpha*255).astype(np.uint8)
        alpha, _ = image_dtype_utils.transform_data_type(alpha,
                                                         to_type=image_dtype_utils.ImageDataType.PILImage)

        # 4. Perform the transformation of the data
        data_to_transform.putalpha(alpha)

        # 5. Convert the transformed image back to the original Data type.
        transformed_data = data_to_transform.copy()
        #transformed_data, _ = image_dtype_utils.transform_data_type(grayscale_image, to_type=input_datatype,
        #                                                            device=device)

        #6. Apply alpha channel to image if given
        additional_data = MLToolkitDictionary({})

        return transformed_data, additional_data