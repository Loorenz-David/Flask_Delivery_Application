from Delivery_app_BK.services.commands.utils import generate_client_id
from Delivery_app_BK.errors import ValidationFailed

def _build_address_object( address:dict | None ):

    if not isinstance( address, dict ): 
        return None
    
    street_address = address.get('address1')
    street2 =  address.get("address2", "")
    if street_address and street2:
        street_address = street_address + ' ' + street2

    latitude = address.get("latitude")
    longitude = address.get("longitude")

    has_coords = latitude is not None and longitude is not None
    has_street = bool(street_address)

    if has_coords and has_street:
        return  {
            "street_address": street_address,
            "city": address.get("city"),
            "country":address.get("country"),
            "postal_code":address.get("zip"),
            "coordinates":{
                "lat":latitude,
                "lng":longitude,
            }
        }
    if has_coords:
        # fix api call to get the street address 
        pass
    if has_street:
        # fix the api call to get the coordinate
        pass

    return None

def _build_phone_object(phone: str | None):
    if not isinstance(phone, str):
        return None
    
    phone_num = phone.strip()
    if phone_num:
        return {
            "prefix":'+',
            "number": phone_num
        }
    
    return None

def _extract_client_fields(shipping_info: dict | None) :
    shipping_info_obj = {}
    if isinstance(shipping_info,dict):
        if shipping_info.get("first_name"):
            shipping_info_obj["client_first_name"] = shipping_info.get("first_name")

        if shipping_info.get("last_name"):
            shipping_info_obj["client_last_name"] = shipping_info.get("last_name")

        phone_obj = _build_phone_object(shipping_info.get("phone"))
        if phone_obj:
            shipping_info_obj["client_primary_phone"] = phone_obj

        if shipping_info.get("email"):
             shipping_info_obj["client_email"] = shipping_info.get("email")

        address_obj = _build_address_object(shipping_info)
        if address_obj:
            shipping_info_obj["client_address"] = address_obj

            
    return shipping_info_obj

def order_mapper(shopify_order):
    if not isinstance(shopify_order, dict):
        raise ValidationFailed('Order must be a dict')
    
    order_object = {
        "client_id": generate_client_id(),
        "reference_number": '#' + str(shopify_order.get("order_number")),
        "external_order_id": str(shopify_order.get("id")),
        "external_source": "shopify",
        "creation_date":shopify_order.get("created_at"),
        "client_email":shopify_order.get("contact_email", shopify_order.get("email")),
        "client_primary_phone":_build_phone_object(shopify_order.get("phone")),
    }

    from_shipping_address = _extract_client_fields( shopify_order.get("shipping_address") )
    from_customer_address = {}
    from_customer = {}

    customer:dict = shopify_order.get("customer")
    if customer:
        from_customer = _extract_client_fields( customer )
        from_customer_address = _extract_client_fields(customer.get("default_address"))
        
    
    order_object = {
        **order_object, 
        **from_customer, 
        **from_customer_address,
        **from_shipping_address
        }
    
    return order_object