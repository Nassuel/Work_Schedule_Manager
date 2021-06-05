import os

rel_path = os.path.dirname(__file__)
file_location = os.path.join(rel_path, "Pictures", "<picture-name>")
pre_file = os.path.join("Pictures", "pre.png") # Rename as desired
out_file = os.path.join("Pictures", "out.png") # Rename as desired

event_info = {
    'subject': '',
    'location': '',
    'recipients': [],
    'attachments': [], # For image to be attached to event`
    'body': '{duration} | {quote}' # Inputs that can be put here | Take off/keep quote if you'd like to not have/add a quote to meeting body
}
