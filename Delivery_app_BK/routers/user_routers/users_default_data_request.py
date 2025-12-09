USER_REQUESTED_DATA = [
    'id',
    'username',
    'email',
    'phone_number',
    'profile_picture',
    {
        'role': [
            'id',
            'role',
            'permisions',
        ],
    },
    {
        'team': [
            'id',
            'name',
            'missing_to_configure',
            'subscription',
        ],
    },
]

TEAM_REQUESTED_DATA = [
    'id',
    'name',
    'missing_to_configure',
    'subscription',
]

USER_ROLE_REQUESTED_DATA = [
    'id',
    'role',
    'permisions',
]

USER_WAREHOUSE_REQUESTED_DATA = [
    'id',
    'name',
    'location',
]
