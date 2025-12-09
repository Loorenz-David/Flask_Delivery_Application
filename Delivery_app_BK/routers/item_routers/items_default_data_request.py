ITEM_REQUESTED_DATA = [
    'id',
    'article_number',
    'order_id',
    'properties',
    'page_link',
    'item_valuation',
    'dimensions',
    'weight',
    'item_position_record',
    'item_state_record',
    'item_type',
    'item_category',
    'item_state_id',
    'item_position_id'
]

ITEM_OPTIONS_REQUESTED_DATA = [
    'id',
    'name',
    {
        'item_types': [
            'id',
            'name',
            'item_category_id',
            {
                'properties': [
                    'id',
                    'name',
                    'field_type',
                    'options',
                    'required',
                ],
            },
        ],
    },
]

ITEM_TYPE_REQUESTED_DATA = [
    'id',
    'name',
    'item_category_id',
    {
        'item_category': [
            'id',
            'name',
        ],
    },
    {
        'properties': [
            'id',
            'name',
            'field_type',
            'options',
            'required',
        ],
    },
]

ITEM_CATEGORY_REQUESTED_DATA = [
    'id',
    'name',
    {
        'item_types': [
            'id',
            'name',
        ],
    },
]

ITEM_PROPERTY_REQUESTED_DATA = [
    'id',
    'name',
    'field_type',
    'options',
    'required',
    {
        'item_types': [
            'id',
            'name',
        ],
    },
]

ITEM_STATE_REQUESTED_DATA = [
    'id',
    'name',
    'color',
    'default',
    'priority',
    'description',
]

ITEM_POSITION_REQUESTED_DATA = [
    'id',
    'name',
    'default',
    'description',
]
