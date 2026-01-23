from datetime import datetime, timezone

def to_datetime( value ):
    date_value = datetime.fromisoformat( value )

    if date_value.tzinfo is None:
        date_value = date_value.replace( tzinfo = timezone.utc )
    

    