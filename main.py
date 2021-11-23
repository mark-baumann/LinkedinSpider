from linkedin import Session

session = Session()

# message = "Hi, I'm Frederik. We may not have met yet, but I'd like to get in touch and see what interesting things you're currently working on.'
message = None

# Generate profile views, by opening unique linked in accounts
session.generate_views(amount=3, sleep=5)

# Start connecting with random people to broaden your network
session.make_contacts(amount=10, message=message, sleep=1)
