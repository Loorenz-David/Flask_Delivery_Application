from Delivery_app_BK.errors import ValidationFailed


def build_dynamic_ids_map(
    instances: list,
    target_key: str = "client_id",
    extract_key: str = "id",
) -> dict:
    if not isinstance(instances, list):
        raise ValidationFailed("Instances must be provided as a list.")

    object_map: dict = {"ids_without_match": []}

    for instance in instances:
        if not hasattr(instance, extract_key):
            raise ValidationFailed(
                f"Instance does not have the attribute '{extract_key}'."
            )
        extract_value = getattr(instance, extract_key)

        if not hasattr(instance, target_key):
            object_map["ids_without_match"].append(extract_value)
            continue

        target_value = getattr(instance, target_key)
        if target_value is None:
            object_map["ids_without_match"].append(extract_value)
            continue

        object_map[target_value] = extract_value

    return object_map
