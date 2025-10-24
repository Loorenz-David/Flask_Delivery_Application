
from typing import List, Dict, Any, Optional, Set

from sqlalchemy.orm.collections import InstrumentedList

from flask_sqlalchemy.model import Model
from typing import Type


class ObjectObtainer:
    """
    The objectObtainer class provides a method to serialize an object's attributes and relationships
    into a dictionary, supporting nested serialization for related objects. It is typically used as a
    mixin for SQLAlchemy models to enable customized dictionary representations, including handling of
    relationships and nested structures.
    """

    def to_dict(
        self,
        columns_to_unpack: List[Any],
        set_of_observations: Optional[Set[str]] = None
    ) -> Dict[str, Any]:
        """
        Serializes the object's specified attributes and relationships into a dictionary.

        Parameters:
            columns_to_unpack (List[Any]): A list of attribute names (str) to include in the output,
                or dictionaries for nested relationships, e.g. [{'relation': [nested_fields]}].
            set_of_observations (Optional[Set[str]]): Used to track already-unpacked attributes to
                prevent duplicates and infinite recursion. Should generally be left as None for top-level calls.

        Returns:
            Dict[str, Any]: A dictionary representation of the object's selected attributes and relationships.

        Raises:
            Exception: If duplicate columns are specified or columns are not wrapped in a list.
            ValueError: If an attribute does not exist on the object.
        """
        unpack_data: Dict[str, Any] = {}

        # Initialize the set to track columns already observed (prevents recursion/duplicates)
        if set_of_observations is None:
            set_of_observations = set()

        # Ensure the columns to unpack is a list
        if isinstance(columns_to_unpack, list):
            for column in columns_to_unpack:

                # Handle nested relationships (dict)
                if isinstance(column, dict):
                   self.unpack_relationship( column, set_of_observations, unpack_data )

                else:
                    # Handle simple attribute (not a nested dict)
                    if not hasattr(self, column):
                        raise ValueError(f"{column} is not a valid attribute (column name) of {self.__class__.__name__}")
                    if column in set_of_observations:
                        raise Exception(f"passed duplicate column in list: {column}")

                    set_of_observations.add(column)
                    unpack_data[column] = getattr(self, column)
        else:
            raise Exception(f"columns passed must be wrap in list: [ <-- {columns_to_unpack} --> ] ")

        return unpack_data
    
    def unpack_relationship(
            self,
            column:Dict,
            set_of_observations:set,
            unpack_data:dict
    ):

        for key, values in column.items():
            # Check for duplicates in observations
            if key in set_of_observations:
                raise Exception(f"passed duplicate column in dictionary: {key}")

            # Ensure the attribute exists
            if not hasattr(self, key):
                raise ValueError(f"no relation with name: {key}")

            target_relation = getattr(self, key)
            set_of_observations.add(key)

            # If the relation is a list (one-to-many/many-to-many)
            if isinstance(target_relation, InstrumentedList):
                list_of_relations = []
                for obj in target_relation:
                    # Recursively call to_dict on related objects
                    list_of_relations.append(obj.to_dict(values))
                unpack_data[key] = list_of_relations
            else:
                # Single related object (one-to-one/many-to-one)
                unpack_data[key] = target_relation.to_dict(values)
