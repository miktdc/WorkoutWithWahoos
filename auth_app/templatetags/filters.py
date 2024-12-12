from django import template

register = template.Library()

@register.filter
def exclude_sign_in_messages(messages):
    return [msg for msg in messages if not msg.message.startswith("Successfully signed in as")]

@register.filter
def get(dictionary, key):
    """Retrieve the value from a dictionary by key."""
    return dictionary.get(key)