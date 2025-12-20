import eventlet
eventlet.monkey_patch()

from application import application  # import your Flask app AFTER monkey_patch