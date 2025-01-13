from pydantic import BaseModel, Field
from typing import Dict, Any


class DynamicLeadModel(BaseModel):
    """Dynamic model for lead data extraction"""

    @classmethod
    def create_model(cls, fields: Dict[str, str]) -> type[BaseModel]:
        """
        Create a dynamic Pydantic model based on user-defined fields

        Args:
            fields: Dictionary of field names and their descriptions
        """
        field_annotations = {}
        field_definitions = {}

        for field_name, description in fields.items():
            field_annotations[field_name] = str
            field_definitions[field_name] = Field(description=description)

        # Create new model dynamically
        return type(
            "LeadData",
            (BaseModel,),
            {"__annotations__": field_annotations, **field_definitions},
        )
