USER_REQUESTED_DATA = [
    'id',
    'username',
    'email',
    'phone_number',
    'profile_picture',
    'show_app_tutorial',
    {
        'role': [
            'id',
            'role',
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
    'description',
    {
        'rules': [
            'id',
            'name',
            'description',
            'rule',
        ],
    },
]

USER_WAREHOUSE_REQUESTED_DATA = [
    'id',
    'name',
    'location',
]

PRINT_TEMPLATE_REQUESTED_DATA = [
    'id',
    'template_string',
    'template_target',
    'timestampt',
    'name'
]
